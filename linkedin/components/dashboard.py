"""
LinkedIn Dashboard Component

This module contains the main LinkedIn dashboard rendering logic.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from linkedin.data.repository import LinkedInRepository
from linkedin.components.kpi_cards import calculate_linkedin_metrics, render_linkedin_kpi_cards
from linkedin.components.charts import (
    render_lead_status_analysis,
    render_top_accounts,
    render_seniority_level_analysis,
    render_analytics_section,
    render_conversion_funnel,
    render_detailed_tables
)
from shared.date_utils import get_date_range, filter_dataframe_by_date
from shared.sound_utils import get_sound_by_name


def render_linkedin_dashboard():
    """Renders the main Linkedin Dashboard interface with advanced analytics"""
    


    # Title
    st.title("🔗 LinkedIn Campaign Analytics")
    # Check for delete success message and display at top
    if 'delete_success' in st.session_state:
        # Add custom CSS for green toast ONLY when showing success
        st.markdown("""
            <style>
            div[data-testid="stToast"] {
                background-color: #d4edda !important;
                border: 1px solid #c3e6cb !important;
                color: #155724 !important;
                font-weight: 500;
            }
            div[data-testid="stToast"] svg {
                fill: #155724 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        success_msg = st.session_state['delete_success']
        
        # Show toast notification immediately (removed duplicate tick from msg)
        st.toast(success_msg, icon="✅")
        
        # Success banner at top of page
        st.markdown(f"""
            <div style="background-color: #d4edda; 
                        border: 1px solid #c3e6cb; 
                        border-radius: 8px; 
                        padding: 16px 24px; 
                        margin-bottom: 24px;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        animation: slideDown 0.4s ease-out;">
                <span style="font-size: 28px;">✅</span>
                <span style="color: #155724; font-weight: 600; font-size: 18px;">
                    {success_msg}
                </span>
            </div>
            <audio autoplay>
                <source src="data:audio/wav;base64,{get_sound_by_name(st.session_state.get('notification_sound_choice', 'Success Chime'))}" type="audio/wav">
            </audio>
            <style>
            @keyframes slideDown {{
                from {{
                    transform: translateY(-30px);
                    opacity: 0;
                }}
                to {{
                    transform: translateY(0);
                    opacity: 1;
                }}
            }}
            </style>
        """, unsafe_allow_html=True)
        
        # Clear the message from session state
        del st.session_state['delete_success']

    # Check for delete error message and display at top
    if 'delete_error' in st.session_state:
        # Add custom CSS for red toast ONLY when showing error
        st.markdown("""
            <style>
            div[data-testid="stToast"] {
                background-color: #f8d7da !important;
                border: 1px solid #f5c6cb !important;
                color: #721c24 !important;
                font-weight: 500;
            }
            div[data-testid="stToast"] svg {
                fill: #721c24 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        error_msg = st.session_state['delete_error']
        
        # Show toast notification immediately (removed duplicate icon from msg)
        st.toast(error_msg, icon="❌")
        
        # Error banner at top of page with SOUND
        st.markdown(f"""
            <div style="background-color: #f8d7da; 
                        border: 1px solid #f5c6cb; 
                        border-radius: 8px; 
                        padding: 16px 24px; 
                        margin-bottom: 24px;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        animation: slideDown 0.4s ease-out;">
                <span style="font-size: 28px;">❌</span>
                <span style="color: #721c24; font-weight: 600; font-size: 18px;">
                    {error_msg}
                </span>
            </div>
            <audio autoplay>
                <source src="data:audio/wav;base64,{get_sound_by_name(st.session_state.get('error_sound_choice', 'Tech Alert'))}" type="audio/wav">
            </audio>
            <style>
            @keyframes slideDown {{
                from {{
                    transform: translateY(-30px);
                    opacity: 0;
                }}
                to {{
                    transform: translateY(0);
                    opacity: 1;
                }}
            }}
            </style>
        """, unsafe_allow_html=True)
        
        # Clear the message from session state
        del st.session_state['delete_error']
    
    
    # Load Data
    try:
        repo = LinkedInRepository()
        campaigns_df = repo.get_campaigns()
        leads_df = repo.get_leads()
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
            custom_start = st.date_input("📅 Start Date", datetime.now().date(), key="li_start")
            custom_start = datetime.combine(custom_start, datetime.min.time())
            custom_end = st.date_input("📅 End Date", datetime.now().date(), key="li_end")
            custom_end = datetime.combine(custom_end, datetime.max.time())

        # Get actual date objects
        start_date, end_date = get_date_range(selected_date_filter, custom_start, custom_end)

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

    # Filter: Only include leads that have replied
    if not leads_df.empty and 'replies' in leads_df.columns:
        leads_df = leads_df[leads_df['replies'] > 0]

    # --- KPI Cards Section ---
    metrics = calculate_linkedin_metrics(campaigns_df)
    
    # ALWAYS calculate total replies from leads table
    # Count leads where replies is not null and > 0
    from linkedin.services.metrics import count_replied_leads, get_replied_leads
    
    total_replied_count = count_replied_leads(leads_df)
    metrics['replies'] = total_replied_count
    
    # Recalculate reply rate with correct count
    if metrics['sent_messages'] > 0:
        metrics['reply_rate'] = (total_replied_count / metrics['sent_messages'] * 100)

    # Calculate Interested Metrics for KPIs using only replied leads
    # Get only leads that have actually replied (replies > 0 and not null)
    replied_leads_df = get_replied_leads(leads_df)
    
    metrics['interested'] = 0
    metrics['interested_reply_rate'] = 0.0

    metrics['objection'] = 0
    metrics['objection_reply_rate'] = 0.0

    metrics['revisit'] = 0
    metrics['revisit_reply_rate'] = 0.0

    metrics['not_interested'] = 0
    metrics['not_interested_reply_rate'] = 0.0
    
    total_replied = len(replied_leads_df)
    
    if not replied_leads_df.empty and 'Status' in replied_leads_df.columns:
        metrics['interested'] = len(replied_leads_df[replied_leads_df['Status'] == 'Interested'])
        metrics['objection'] = len(replied_leads_df[replied_leads_df['Status'].isin(['Objection', 'Objections'])])
        metrics['revisit'] = len(replied_leads_df[replied_leads_df['Status'] == 'Revisit Later'])
        metrics['not_interested'] = len(replied_leads_df[replied_leads_df['Status'] == 'Not Interested'])
        
        # Calculate rates based on total replied leads (not all leads)
        if total_replied > 0:
            metrics['interested_reply_rate'] = (metrics['interested'] / total_replied * 100)
            metrics['objection_reply_rate'] = (metrics['objection'] / total_replied * 100)
            metrics['revisit_reply_rate'] = (metrics['revisit'] / total_replied * 100)
            metrics['not_interested_reply_rate'] = (metrics['not_interested'] / total_replied * 100)

    
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
    accounts_df = repo.get_accounts()
    render_top_accounts(leads_df, accounts_df)
    
    st.divider()
    
    # Section 3: Campaign Effectiveness (Styles Removed)
    # render_campaign_effectiveness(campaigns_df, leads_df)
    
    # st.divider()
    
    # Section 4: Seniority Level Analysis
    if not leads_df.empty and ('Seniority' in leads_df.columns or 'job_title' in leads_df.columns):
        # st.markdown("## 💼 Audience Insights") # Handled inside the function now
        render_seniority_level_analysis(leads_df)
        st.divider()
    
    # Analytics section already imported at top
    
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
