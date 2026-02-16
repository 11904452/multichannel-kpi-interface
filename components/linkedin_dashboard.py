import streamlit as st
import pandas as pd
from datetime import datetime
from data.linkedin_data import LinkedinDataLoader
from components.linkedin_kpis import calculate_linkedin_metrics, render_linkedin_kpi_cards
from components.linkedin_charts import (
    render_lead_status_analysis,
    render_top_accounts,
    render_seniority_level_analysis,
    render_analytics_section,
    render_conversion_funnel,
    render_detailed_tables
)
from utils.date_utils import get_date_range, filter_dataframe_by_date

def render_linkedin_dashboard():
    """Renders the main Linkedin Dashboard interface with advanced analytics"""
    
    # Enhanced header with gradient
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0077B5 0%, #00A0DC 100%); 
                padding: 30px; border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; text-align: center; font-size: 2.5em;'>
            🔗 LinkedIn Campaign Analytics
        </h1>
        <p style='color: rgba(255,255,255,0.9); text-align: center; margin: 10px 0 0 0; font-size: 1.2em;'>
            Comprehensive Performance Insights & Lead Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load Data
    try:
        campaigns_df = LinkedinDataLoader.get_linkedin_campaigns()
        leads_df = LinkedinDataLoader.get_linkedin_leads()
    except Exception as e:
        st.error(f"Error loading Linkedin data: {str(e)}")
        return

    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("🎯 Filters")
        
        # 1. Workspace Filter
        ws_list = ["All Workspaces"]
        if not campaigns_df.empty and 'workspace_name' in campaigns_df.columns:
            ws_list += sorted(campaigns_df['workspace_name'].dropna().unique().tolist())
            
        selected_ws = st.selectbox("Select Workspace", ws_list, key="li_workspace")
        
        # Filter campaigns by workspace for the next selector
        filtered_campaigns_choices = campaigns_df
        if selected_ws != "All Workspaces":
            filtered_campaigns_choices = campaigns_df[campaigns_df['workspace_name'] == selected_ws]

        # 2. Campaign Filter
        campaign_list = ["All Campaigns"]
        if not filtered_campaigns_choices.empty and 'campaign_name' in filtered_campaigns_choices.columns:
             campaign_list += sorted(filtered_campaigns_choices['campaign_name'].dropna().unique().tolist())
             
        selected_campaign = st.selectbox("Select Campaign", campaign_list, key="li_campaign")

        # 3. Date Filter
        date_options = [
            "Today", "This Week", "Last Week", "Last 7 Days", 
            "Last 30 Days", "This Month", "Last Month", "All Time", "Custom Date Range"
        ]
        
        selected_date_filter = st.selectbox(
            "Reply Date Range",
            options=date_options,
            index=7,  # Default: All Time
            key="li_date_filter"
        )
        
        custom_start, custom_end = None, None
        if selected_date_filter == "Custom Date Range":
            col1, col2 = st.columns(2)
            with col1:
                custom_start = st.date_input("Start", datetime.now().date(), key="li_start")
                custom_start = datetime.combine(custom_start, datetime.min.time())
            with col2:
                custom_end = st.date_input("End", datetime.now().date(), key="li_end")
                custom_end = datetime.combine(custom_end, datetime.max.time())

        # Get actual date objects
        start_date, end_date = get_date_range(selected_date_filter, custom_start, custom_end)
        
        # Ensure dates are timezone-aware (UTC) to match dataframe
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)

        st.divider()
        
        # Active filters summary with enhanced styling
        st.markdown("### 📌 Active Filters")
        if selected_ws != "All Workspaces":
            st.markdown(f"**Workspace:** `{selected_ws}`")
        if selected_campaign != "All Campaigns":
            st.markdown(f"**Campaign:** `{selected_campaign}`")
        if selected_date_filter != "All Time":
            st.markdown(f"**Date:** `{start_date.strftime('%Y-%m-%d')}` to `{end_date.strftime('%Y-%m-%d')}`")

        # --- Campaign Actions ---
        if selected_campaign != "All Campaigns":
            st.divider()
            st.markdown("### ⚠️ Danger Zone")
            
            # Use columns for better layout
            col_del1, col_del2 = st.columns([0.1, 0.9])
            
            enable_delete = st.checkbox("Enable Deletion", key="enable_del_cam")
            
            if enable_delete:
                if st.button("🗑️ Delete Campaign", type="primary", use_container_width=True):
                    # Get campaign ID
                    params = filtered_campaigns_choices[filtered_campaigns_choices['campaign_name'] == selected_campaign]
                    if not params.empty:
                        campaign_id = params.iloc[0]['campaign_id']
                        
                        with st.spinner("Deleting campaign data..."):
                            if LinkedinDataLoader.delete_campaign(campaign_id):
                                st.success(f"Campaign '{selected_campaign}' deleted successfully!")
                                st.cache_data.clear()
                                import time
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("Failed to delete campaign.")
                    else:
                        st.error("Campaign ID not found.")

    # --- Apply Filters to Data ---
    
    # Store original data for some comparisons
    original_campaigns_df = campaigns_df.copy()
    original_leads_df = leads_df.copy()
    
    # Filter 1: Workspace
    if selected_ws != "All Workspaces":
        campaigns_df = campaigns_df[campaigns_df['workspace_name'] == selected_ws]
        
    # Filter 2: Campaign
    if selected_campaign != "All Campaigns":
        campaigns_df = campaigns_df[campaigns_df['campaign_name'] == selected_campaign]

    # Filter Leads based on remaining campaigns
    if not campaigns_df.empty:
        valid_ids = campaigns_df['campaign_id'].astype(str).unique()
        leads_df = leads_df[leads_df['campaign_id'].astype(str).isin(valid_ids)]
    else:
        leads_df = pd.DataFrame(columns=leads_df.columns)

    # Filter 3: Date (Applied to Leads 'reply_date')
    if selected_date_filter != "All Time" and not leads_df.empty and 'reply_date' in leads_df.columns:
        leads_df = filter_dataframe_by_date(leads_df, 'reply_date', start_date, end_date)

    # --- KPI Cards Section ---
    metrics = calculate_linkedin_metrics(campaigns_df)
    
    # If date filter is active, update replies based on filtered leads
    if selected_date_filter != "All Time":
         filtered_replies = leads_df['replies'].sum() if not leads_df.empty and 'replies' in leads_df.columns else 0
         metrics['replies'] = filtered_replies
         if metrics['sent_messages'] > 0:
             metrics['reply_rate'] = (filtered_replies / metrics['sent_messages'] * 100)

    # Calculate Interested Metrics for KPIs
    metrics['interested'] = 0
    metrics['interested_reply_rate'] = 0.0

    metrics['objection'] = 0
    metrics['objection_reply_rate'] = 0.0

    metrics['revisit'] = 0
    metrics['revisit_reply_rate'] = 0.0

    metrics['not_interested'] = 0
    metrics['not_interested_reply_rate'] = 0.0
    
    if not leads_df.empty and 'Status' in leads_df.columns:
        metrics['interested'] = len(leads_df[leads_df['Status'] == 'Interested'])
        metrics['objection'] = len(leads_df[leads_df['Status'].isin(['Objection', 'Objections'])])
        metrics['revisit'] = len(leads_df[leads_df['Status'] == 'Revisit Later'])
        metrics['not_interested'] = len(leads_df[leads_df['Status'] == 'Not Interested'])
        # Calculate rate based on sent messages (standard denominator for reply rates)
        if metrics['replies'] > 0:
             metrics['interested_reply_rate'] = (metrics['interested'] / metrics['replies'] * 100)
             metrics['objection_reply_rate'] = (metrics['objection'] / metrics['replies'] * 100)
             metrics['revisit_reply_rate'] = (metrics['revisit'] / metrics['replies'] * 100)
             metrics['not_interested_reply_rate'] = (metrics['not_interested'] / metrics['replies'] * 100)

    
    render_linkedin_kpi_cards(metrics)
    
    st.divider()

    # --- Main Analytics Sections ---
    
    # Section 1: Conversion Funnel & Lead Status
    st.markdown("## 🎯 Performance Overview")
    render_conversion_funnel(campaigns_df, leads_df)
    
    st.divider()
    
    render_lead_status_analysis(leads_df)
    
    st.divider()
    
    # Section 2: Top Performers
    st.markdown("## 🏆 Performance Leaders")
    render_top_accounts(leads_df)
    
    st.divider()
    
    # Section 3: Campaign Effectiveness (Styles Removed)
    # render_campaign_effectiveness(campaigns_df, leads_df)
    
    # st.divider()
    
    # Section 4: Seniority Level Analysis
    if not leads_df.empty and 'job_title' in leads_df.columns:
        # st.markdown("## 💼 Audience Insights") # Handled inside the function now
        render_seniority_level_analysis(leads_df)
        st.divider()
    
    from components.linkedin_charts import render_analytics_section
    
    # Section 5: Analytics (Replaces Engagement Trends)
    if not leads_df.empty and 'reply_date' in leads_df.columns:
        # st.markdown("## 📈 Engagement Trends") # Header moved inside component for better control
        render_analytics_section(leads_df)
        st.divider()
    
    # Section 6: Detailed Tables
    st.markdown("## 📋 Detailed Data")
    render_detailed_tables(campaigns_df, leads_df)
    
    # Footer with summary stats
    # st.markdown("---")
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     st.metric("Total Campaigns", len(campaigns_df))
    # with col2:
    #     st.metric("Total Leads", len(leads_df))
    # with col3:
    #     total_sent = campaigns_df['sent_connections'].sum() if not campaigns_df.empty else 0
    #     st.metric("Connections Sent", f"{int(total_sent):,}")
    # with col4:
    #     total_replies = campaigns_df['replies'].sum() if not campaigns_df.empty else 0
    #     st.metric("Total Replies", f"{int(total_replies):,}")
