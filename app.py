import streamlit as st
from data.airtable_client import AirtableClient
from data.data_processor import DataProcessor
from components.filters import render_workspace_filters, render_campaign_filters
from components.kpi_cards import render_kpi_cards
from components.charts import render_charts, render_interested_leads_table
from components.sequence_stats import render_sequence_stats
from utils.date_utils import filter_dataframe_by_date
from utils.metrics import calculate_kpis, calculate_campaign_kpis
from components.guide import render_math_guide
import pandas as pd

# Page config
st.set_page_config(
    page_title="📧 Email Campaign KPI Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS for enhanced UI with modern aesthetics
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global font and smoothing */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main container with animated gradient background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientShift 15s ease infinite;
        padding: 2rem;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glassmorphism container for content */
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Header styling with gradient text */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 2.5em !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.5px;
        animation: fadeInDown 0.6s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    h2, h3 {
        color: #1e293b;
        font-weight: 700;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Subheader with decorative animated element */
    .stMarkdown h2::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-right: 12px;
        border-radius: 2px;
        vertical-align: middle;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* Enhanced divider with glow effect */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.6), transparent);
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar with glassmorphism */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar text color adjustments */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] p {
        color: white !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced button styling with 3D effect */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    
    
    /* Sidebar button specific styling - pill-shaped like platform selector */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        font-weight: 500 !important;
        font-size: 0.95em !important;
        padding: 0.65rem 1.2rem !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
        backdrop-filter: blur(10px) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        color: white !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:active {
        transform: translateX(3px) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Force button text color in sidebar to white */
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span,
    [data-testid="stSidebar"] .stButton > button div {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover p,
    [data-testid="stSidebar"] .stButton > button:hover span,
    [data-testid="stSidebar"] .stButton > button:hover div {
        color: white !important;
    }
    
    /* Modern tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        padding: 8px;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Enhanced dataframe with glassmorphism */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Plotly chart container with enhanced shadow */
    .js-plotly-plot {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        background: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .js-plotly-plot:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    /* Metric cards enhancement */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    /* Date input styling */
    .stDateInput > div > div {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Smooth scroll behavior */
    html {
        scroll-behavior: smooth;
    }
    
    /* Loading animation enhancement */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Info/Warning/Error boxes with glassmorphism */
    .stAlert {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border-left: 4px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load and process data from Airtable"""
    try:
        client = AirtableClient()
    except Exception as e:
        st.error(f"Failed to connect to Airtable: {e}")
        st.stop()
        
    with st.spinner("Loading dashboard data..."):
        # Fetch campaigns
        campaigns_raw = client.get_campaigns()
        campaigns_df = DataProcessor.process_campaigns(campaigns_raw)
        
        # Fetch leads
        leads_raw = client.get_leads()
        leads_df = DataProcessor.process_leads(leads_raw)

        # Fetch sequences
        sequences_raw = client.get_email_sequences()
        sequences_df = DataProcessor.process_email_sequences(sequences_raw)
        
    return campaigns_df, leads_df, sequences_df

def render_workspace_overview(campaigns_df: pd.DataFrame, leads_df: pd.DataFrame):
    """Render the workspace overview tab"""
    st.header("📊 Workspace Overview")
    
    # Render workspace filter
    selected_workspace = render_workspace_filters(campaigns_df)
    
    # Filter data by workspace
    filtered_campaigns_df = campaigns_df.copy()
    filtered_leads_df = leads_df.copy()
    
    if not campaigns_df.empty:
        # Filter campaigns by workspace
        if selected_workspace != "All Workspaces":
            filtered_campaigns_df = campaigns_df[campaigns_df['workspace_name'] == selected_workspace]
        
        # Filter leads by campaigns in the workspace
        if not filtered_campaigns_df.empty and 'campaign_id' in filtered_campaigns_df.columns:
            valid_campaign_ids = set(filtered_campaigns_df['campaign_id'].dropna().unique())
            
            if 'campaign_id' in filtered_leads_df.columns and not filtered_leads_df.empty:
                # vectorized filtering is now safe due to DataProcessor fixes
                filtered_leads_df = filtered_leads_df[filtered_leads_df['campaign_id'].isin(valid_campaign_ids)]
    
    # Calculate current metrics
    current_metrics = calculate_kpis(filtered_campaigns_df)
    
    # Calculate previous metrics (using all data for comparison)
    # For workspace view, we compare against the same workspace's historical data
    # Since we don't have time-based filtering here, we use the same data
    previous_metrics = calculate_kpis(filtered_campaigns_df)
    
    # Render KPI Cards
    render_kpi_cards(current_metrics, previous_metrics)
    
    # Render Charts
    render_charts(filtered_leads_df, filtered_campaigns_df, key_prefix="workspace")

def render_campaign_analysis(campaigns_df: pd.DataFrame, leads_df: pd.DataFrame, sequences_df: pd.DataFrame):
    """Render the campaign analysis tab"""
    st.header("🔍 Campaign Analysis")
    
    # Render campaign filters
    # Render campaign filters
    # Get the workspace selected in the first tab (if available)
    current_workspace = st.session_state.get("workspace_filter", "All Workspaces")
    selected_campaign, start_date, end_date = render_campaign_filters(campaigns_df, workspace=current_workspace)
    
    # Check if valid campaign selected
    if selected_campaign == "No campaigns available" or not selected_campaign:
        st.warning("No campaigns available for analysis. Please check your data.")
        return
    
    # Filter campaigns to get the selected campaign
    campaign_data = campaigns_df[campaigns_df['Name'] == selected_campaign]
    
    if campaign_data.empty:
        st.warning(f"Campaign '{selected_campaign}' not found.")
        return
    
    campaign_row = campaign_data.iloc[0]
    
    # Filter leads for this campaign and date range
    filtered_leads_df = leads_df.copy()
    
    if not filtered_leads_df.empty and 'campaign_id' in campaign_data.columns:
        campaign_id = int(campaign_row['campaign_id'])
        
        if 'campaign_id' in filtered_leads_df.columns:
            # Direct vectorized filtering (safe now that IDs are numeric)
            filtered_leads_df = filtered_leads_df[filtered_leads_df['campaign_id'] == campaign_id]
        
        # Apply date filter
        if 'Date' in filtered_leads_df.columns:
            filtered_leads_df = filter_dataframe_by_date(filtered_leads_df, 'Date', start_date, end_date)
    
    # Calculate current period metrics
    current_metrics = calculate_campaign_kpis(campaign_row)
    
    # Calculate previous period metrics
    duration = end_date - start_date
    prev_end = start_date - pd.Timedelta(seconds=1)
    prev_start = prev_end - duration
    
    # For previous period, we use the same campaign data
    # (In a real scenario, you might want to calculate based on previous period's activity)
    previous_metrics = calculate_campaign_kpis(campaign_row)
    
    # Render KPI Cards
    st.subheader(f"Campaign: {selected_campaign}")
    render_kpi_cards(current_metrics, previous_metrics)
    
    # Render Charts (only for this campaign)
    campaign_df_single = pd.DataFrame([campaign_row])
    render_charts(filtered_leads_df, campaign_df_single, key_prefix="campaign")
    
    # Render Interested Leads Table (Specific to Campaign Analysis)
    render_interested_leads_table(filtered_leads_df, campaigns_df)

    # Render Sequence Stats
    # Filter sequences for this campaign
    st.divider()
    campaign_sequences = pd.DataFrame()
    if not sequences_df.empty and 'campaign_id' in sequences_df.columns:
        # Handle potential type mismatch (int vs float vs str) by converting to numeric where possible
        # campaign_row['campaign_id'] might be float/int.
        cid = campaign_row.get('campaign_id')
        if cid is not None:
            # Ensure filtering works if types differ
            # Safe way: match as strings or match as numeric?
            # Users said campaign_id is Number.
            # sequences_df['campaign_id'] is numeric (0 filled).
            try:
                cid_num = float(cid)
                campaign_sequences = sequences_df[sequences_df['campaign_id'] == cid_num]
            except:
                # Fallback if cid is string that can't be float
                campaign_sequences = sequences_df[sequences_df['campaign_id'].astype(str) == str(cid)]
    
    render_sequence_stats(filtered_leads_df, campaign_sequences, campaign_stats=campaign_row)

def run_email_dashboard():
    # Title
    st.title("📧 Email Campaign KPI Dashboard")
    
    # Load data once
    campaigns_df, leads_df, sequences_df = load_data()
    
    # --- Navigation State Management ---
    TABS = ["🏠 Workspace Overview", "🔍 Campaign Analysis"]
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = TABS[0]
        
    def switch_to_analysis():
        """Callback to switch to analysis tab"""
        st.session_state.active_tab = TABS[1]

    # --- Global Sidebar Filters ---
    # We render filters here to unify the control logic
    with st.sidebar:
        # 1. Workspace Filter (Always visible)
        # We need to manually call the logic here or reuse the component.
        # But 'render_workspace_filters' is designed to return the value.
        # Let's use it.
        st.header("Filters")
        
        # Workspace selection
        workspaces = ["All Workspaces"]
        if not campaigns_df.empty and 'workspace_name' in campaigns_df.columns:
            unique_ws = sorted(campaigns_df['workspace_name'].dropna().unique().tolist())
            workspaces.extend(unique_ws)
            
        selected_workspace = st.selectbox(
            "Select Workspace", 
            options=workspaces, 
            index=0, 
            key="workspace_filter"
        )
        st.caption(f"Viewing: {selected_workspace}")
        st.divider()

        # 2. Campaign Filter (Visible now, triggers redirect)
        # We call render_campaign_filters but pass the logic
        # Note: render_campaign_filters normally creates its own sidebar header. 
        # We might want to adjust that or just let it be.
        # Ideally we refactored render_campaign_filters to NOT create a header if we want clean UI, 
        # but for now we just use it.
    
    # Filter Campaign Data based on Workspace for the Selector
    # Passing on_change to trigger redirect
    selected_campaign, start_date, end_date = render_campaign_filters(
        campaigns_df, 
        workspace=selected_workspace, 
        on_change=switch_to_analysis
    )
        
    # --- Main Content Area ---
    # Custom CSS for the radio button to look like tabs/pills
    st.markdown("""
    <style>
        /* Hide the default radio circles */
        div[data-testid="stRadio"] > div {
            flex-direction: row;
            gap: 10px;
        }
        div[data-testid="stRadio"] label > div:first-child {
            display: None;
        }
        
        /* Base style for the labels (tabs) */
        div[data-testid="stRadio"] label {
            background-color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            color: #64748b;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        /* Hover state */
        div[data-testid="stRadio"] label:hover {
            border-color: #cbd5e1;
            transform: translateY(-1px);
        }

        /* Active State - We rely on Streamlit adding a specific class or structure 
           Usually checking input state is hard in pure CSS for parents.
           However, Streamlit active radio items often have a specific structure.
           The easiest way is to target the span inside that has specific text color or check aria-checked.
           BUT Streamlit's radio implementation structure changes.
           A robust way is hard without :has(), but :has() is supported in modern browsers.
        */
        
        /* Target label containing checked input */
        div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Fallback for older browsers (though :has is widely supported now)
           We can try to style the div inside if possible, but that doesn't style the whole container.
           For now :has is the best bet for this "pill" look on container.
        */
        
        /* Adjust text color inside active tab */
        div[data-testid="stRadio"] label:has(input:checked) p {
            color: white !important;
        }
        
    </style>
    """, unsafe_allow_html=True)

    # Use radio with horizontal=True to mock tabs, controlled by session state
    active_tab = st.radio(
        "Navigation", 
        TABS, 
        key="active_tab", 
        horizontal=True,
        label_visibility="collapsed"
    )

    if active_tab == TABS[0]:
        # Workspace Overview
        # st.header("📊 Workspace Overview") # Removed as requested
        
        # Filter data by workspace (Logic moved from render_workspace_overview)
        filtered_campaigns_df = campaigns_df.copy()
        filtered_leads_df = leads_df.copy()
        
        if not campaigns_df.empty:
            if selected_workspace != "All Workspaces":
                filtered_campaigns_df = campaigns_df[campaigns_df['workspace_name'] == selected_workspace]
            
            if not filtered_campaigns_df.empty and 'campaign_id' in filtered_campaigns_df.columns:
                valid_campaign_ids = set(filtered_campaigns_df['campaign_id'].dropna().unique())
                if 'campaign_id' in filtered_leads_df.columns and not filtered_leads_df.empty:
                     filtered_leads_df = filtered_leads_df[filtered_leads_df['campaign_id'].isin(valid_campaign_ids)]
        
        current_metrics = calculate_kpis(filtered_campaigns_df)
        previous_metrics = calculate_kpis(filtered_campaigns_df) # Simplified prev
        
        render_kpi_cards(current_metrics, previous_metrics)
        render_charts(filtered_leads_df, filtered_campaigns_df, key_prefix="workspace")

    elif active_tab == TABS[1]:
        # Campaign Analysis
        # st.header("🔍 Campaign Analysis") # Removed as requested
        
        # Filters already rendered globally.
        # render_campaign_analysis logic needs to be inline or adjusted to not re-render filters.
        
        if selected_campaign == "No campaigns available" or not selected_campaign:
            st.warning("No campaigns available regarding the filters.")
        else:
            # Filter campaigns
            campaign_data = campaigns_df[campaigns_df['Name'] == selected_campaign]
            
            if campaign_data.empty:
                st.warning(f"Campaign '{selected_campaign}' not found.")
            else:
                campaign_row = campaign_data.iloc[0]
                
                # Filter leads
                filtered_leads_df = leads_df.copy()
                if not filtered_leads_df.empty and 'campaign_id' in campaign_data.columns:
                    campaign_id = int(campaign_row['campaign_id'])
                    if 'campaign_id' in filtered_leads_df.columns:
                        filtered_leads_df = filtered_leads_df[filtered_leads_df['campaign_id'] == campaign_id]
                    if 'Date' in filtered_leads_df.columns:
                        filtered_leads_df = filter_dataframe_by_date(filtered_leads_df, 'Date', start_date, end_date)
                
                # Metrics
                current_metrics = calculate_campaign_kpis(campaign_row)
                previous_metrics = calculate_campaign_kpis(campaign_row)
                
                st.subheader(f"Campaign: {selected_campaign}")
                render_kpi_cards(current_metrics, previous_metrics)
                
                campaign_df_single = pd.DataFrame([campaign_row])
                render_charts(filtered_leads_df, campaign_df_single, key_prefix="campaign")
                
                render_interested_leads_table(filtered_leads_df, campaigns_df)

                # Sequence Stats
                st.divider()
                campaign_sequences = pd.DataFrame()
                if not sequences_df.empty and 'campaign_id' in sequences_df.columns:
                     cid = campaign_row.get('campaign_id')
                     if cid is not None:
                         try:
                             cid_num = float(cid)
                             campaign_sequences = sequences_df[sequences_df['campaign_id'] == cid_num]
                         except:
                             campaign_sequences = sequences_df[sequences_df['campaign_id'].astype(str) == str(cid)]
                
                render_sequence_stats(filtered_leads_df, campaign_sequences, campaign_stats=campaign_row)

    # Refresh button in sidebar (Bottom)
    with st.sidebar:
        st.divider()
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
            
        # Math Guide
        render_math_guide()

def main():
    # Sidebar Platform Selection with Enhanced Toggle
    with st.sidebar:
        # Custom CSS for segmented control toggle
        st.markdown("""
        <style>
        /* Segmented Control Styling */
        div[data-testid="stRadio"][data-baseweb="radio"] > div {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 4px;
            gap: 4px;
        }
        
        div[data-testid="stRadio"] > div > label {
            background-color: transparent;
            border-radius: 8px;
            padding: 12px 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 600;
            text-align: center;
            border: none;
            margin: 0;
        }
        
        div[data-testid="stRadio"] > div > label:hover {
            background-color: rgba(255, 255, 255, 0.15);
            color: white;
        }
        
        div[data-testid="stRadio"] > div > label[data-baseweb="radio"] > div:first-child {
            display: none;
        }
        
        /* Active state */
        div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        div[data-testid="stRadio"] label:has(input:checked) p {
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0; font-size: 1.8em;'>🚀 Dashboard</h2>
            <p style='color: rgba(255,255,255,0.7); font-size: 0.9em; margin: 5px 0 0 0;'>Select Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Platform selector with horizontal layout
        platform = st.radio(
            "platform_selector_label",
            ["📧 Email", "🔗 LinkedIn"],
            index=0,
            key="platform_selector",
            horizontal=True,
            label_visibility="collapsed"
        )
        st.divider()

    if platform == "🔗 LinkedIn":
        from components.linkedin_dashboard import render_linkedin_dashboard
        render_linkedin_dashboard()
    else:
        run_email_dashboard()

if __name__ == "__main__":
    main()
