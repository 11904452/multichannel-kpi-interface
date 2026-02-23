import streamlit as st
import pandas as pd
from core.database import get_database_client
from shared.ui_components import show_success, show_error
from email_campaigns.data.repository import EmailRepository
from config import EMAIL_API_KEYS_TABLE_NAME


def check_for_missing_keys() -> bool:
    """
    Check if there are any discovered workspaces without API keys.
    Returns True if attention is needed.
    """
    try:
        db = get_database_client()
        repo = EmailRepository()
        
        # 1. Get Discovered Workspaces
        campaigns = repo.get_campaigns()
        if not campaigns:
            return False
            
        camp_df = pd.DataFrame(campaigns)
        discovered_ids = set()
        
        if 'workspace_id' in camp_df.columns:
            # Filter out None/Nan
            discovered_ids = set(camp_df['workspace_id'].dropna().astype(str).unique())
        
        if not discovered_ids:
            return False
            
        # 2. Get Configured Keys
        # We only care about keys that are NOT null/empty
        keys_response = db.client.table(EMAIL_API_KEYS_TABLE_NAME).select("workspace_id, api_key").execute()
        configured_ids = set()
        if keys_response.data:
            for k in keys_response.data:
                # Check if key is valid (not null/empty/{})
                val = k.get('api_key')
                if val and str(val).strip() != '{}':
                    configured_ids.add(str(k.get('workspace_id')))
        
        # 3. Check for missing
        # If any discovered ID is NOT in configured IDs, return True
        missing = discovered_ids - configured_ids
        
        # Filter out "UNKNOWN" or empty strings if they strictly exist
        missing = {x for x in missing if x and x != 'nan' and x.lower() != 'unknown' and x.lower() != 'none'}
        
        return len(missing) > 0
        
    except Exception as e:
        # If error, fail safe (don't show alert)
        return False


def render_api_key_manager():
    """Render the API Key Management Interface"""
    
    st.markdown("""
    <div style='background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%); 
                padding: 30px; border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; text-align: center; font-size: 2.5em;'>
            🔑 API Key Management
        </h1>
        <p style='color: rgba(255,255,255,0.9); text-align: center; margin: 10px 0 0 0; font-size: 1.2em;'>
            Manage Workspace API Keys
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    db = get_database_client()
    table_name = EMAIL_API_KEYS_TABLE_NAME
    
    # Initialize session state for editing
    if "edit_ws_id" not in st.session_state:
        st.session_state.edit_ws_id = ""
        st.session_state.edit_ws_name = ""
    
    # --- Fetch Data ---
    with st.spinner("Loading Workspaces..."):
        # 1. Get existing keys
        try:
            keys_response = db.client.table(table_name).select("*").execute()
            existing_keys = keys_response.data
            keys_df = pd.DataFrame(existing_keys) if existing_keys else pd.DataFrame(columns=['workspace_id', 'workspace_name', 'api_key', 'id'])
        except Exception as e:
            st.error(f"Error fetching keys: {e}")
            existing_keys = []
            keys_df = pd.DataFrame()

        # 2. Get Workspaces from Campaigns (Discovery)
        repo = EmailRepository()
        campaigns = repo.get_campaigns()
        
        discovered_workspaces = []
        if campaigns:
            camp_df = pd.DataFrame(campaigns)
            # Check for workspace columns
            if 'workspace_id' in camp_df.columns and 'workspace_name' in camp_df.columns:
                discovered_workspaces = camp_df[['workspace_id', 'workspace_name']].drop_duplicates().to_dict('records')
            elif 'workspace_name' in camp_df.columns:
                # Fallback if ID missing
                discovered_workspaces = camp_df[['workspace_name']].drop_duplicates().to_dict('records')
                for d in discovered_workspaces:
                    d['workspace_id'] = "UNKNOWN"
        
        # Merge Discovered with Existing
        # We want a master list of all workspaces (from DB keys OR from campaigns)
        
        master_list = {} # Key: workspace_id (or name if id missing)
        
        # Add discovered first
        for ws in discovered_workspaces:
            wid = str(ws.get('workspace_id', 'UNKNOWN'))
            wname = ws.get('workspace_name', 'Unknown')
            master_list[wid] = {
                'workspace_id': wid,
                'workspace_name': wname,
                'has_key': False,
                'db_id': None,
                'api_key': None
            }
            
        # Update with existing keys
        for key in existing_keys:
            wid = str(key.get('workspace_id', 'UNKNOWN'))
            current_api_val = key.get('api_key')
            has_api_key = bool(current_api_val and str(current_api_val).strip() != '{}')
            
            if wid in master_list:
                master_list[wid]['has_key'] = has_api_key
                master_list[wid]['db_id'] = key.get('id')
                master_list[wid]['api_key'] = current_api_val
                # Update name if DB has better name? Or keep campaign name?
                # Usually DB config might be more manual/correct.
                if key.get('workspace_name'):
                     master_list[wid]['workspace_name'] = key.get('workspace_name')
            else:
                # Key exists but no campaigns found for it yet (maybe new workspace)
                master_list[wid] = {
                    'workspace_id': wid,
                    'workspace_name': key.get('workspace_name', 'Unknown'),
                    'has_key': has_api_key,
                    'db_id': key.get('id'),
                    'api_key': current_api_val
                }
    
    # --- Add/Edit Form ---
    # Determine if we are editing/adding based on session state or user action
    with st.expander("➕ Add / Edit API Key", expanded=bool(st.session_state.edit_ws_id)):
        with st.form("api_key_form"):
            col1, col2 = st.columns(2)
            with col1:
                workspace_name = st.text_input("Workspace Name", value=st.session_state.edit_ws_name, placeholder="e.g. Sales Team A")
            with col2:
                workspace_id = st.text_input("Workspace ID", value=st.session_state.edit_ws_id, placeholder="e.g. ws_12345")
                
            api_key_input = st.text_input("API Key", placeholder="Enter API Key", type="password")
            
            submitted = st.form_submit_button("Save Key")
            
            if submitted:
                if not workspace_name or not workspace_id:
                    show_error("Workspace Name and ID are required")
                else:
                    try:
                        # Check if update or insert - query DB directly for robust check
                        # Check if workspace_id already exists in the table
                        check_res = db.client.table(table_name).select('id').eq('workspace_id', workspace_id).execute()
                        
                        data = {
                            "workspace_name": workspace_name,
                            "workspace_id": workspace_id,
                            "api_key": api_key_input
                        }
                        
                        if check_res.data:
                            # Update existing record
                            existing_id = check_res.data[0]['id']
                            db.client.table(table_name).update(data).eq('id', existing_id).execute()
                            show_success(f"Updated keys for {workspace_name}")
                        else:
                            # Insert new record
                            db.client.table(table_name).insert(data).execute()
                            show_success(f"Added keys for {workspace_name}")
                            
                        # Clear edit state
                        st.session_state.edit_ws_id = ""
                        st.session_state.edit_ws_name = ""
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        show_error(f"Failed to save: {str(e)}")

    # --- List View ---
    st.subheader("📋 Workspace Configuration")
    
    if not master_list:
        st.info("No workspaces found.")
    else:
        # Sort by Name
        sorted_ws = sorted(master_list.values(), key=lambda x: x['workspace_name'])
        
        # Headers
        c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
        c1.markdown("**Workspace Name**")
        c2.markdown("**ID**")
        c3.markdown("**Status**")
        c4.markdown("**Actions**")
        st.divider()
        
        for item in sorted_ws:
            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
            
            with c1:
                st.write(item['workspace_name'])
            with c2:
                st.code(item['workspace_id'])
            with c3:
                if item['has_key']:
                    st.success("✅ Configured")
                else:
                    st.warning("⚠️ Missing Key")
                    
            with c4:
                # ACTION BUTTONS
                col_a, col_b = st.columns(2)
                with col_a:
                    btn_label = "✏️ Edit" if item['has_key'] else "➕ Add Key"
                    if st.button(btn_label, key=f"btn_edit_{item['workspace_id']}"):
                        st.session_state.edit_ws_id = item['workspace_id']
                        st.session_state.edit_ws_name = item['workspace_name']
                        st.rerun()
                
                with col_b:
                    if item['has_key']:
                        if st.button("🗑️", key=f"btn_del_{item['workspace_id']}", help="Delete Configuration"):
                            try:
                                db.client.table(table_name).delete().eq("id", item['db_id']).execute()
                                show_success("Deleted")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                show_error(f"Error: {e}")
            
            st.divider()
