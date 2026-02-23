"""
Email Dashboard Component

This module contains the main email dashboard rendering logic,
extracted from the original app.py for better organization.
"""

import streamlit as st
import pandas as pd

from email_campaigns.data.repository import EmailRepository
from email_campaigns.data.processor import DataProcessor
from email_campaigns.components.filters import render_workspace_filters, render_campaign_filters
from email_campaigns.components.kpi_cards import render_kpi_cards
from email_campaigns.components.charts import render_charts, render_interested_leads_table
from email_campaigns.components.sequence_stats import render_sequence_stats
from email_campaigns.services.metrics import calculate_kpis, calculate_campaign_kpis, calculate_filtered_kpis, calculate_filtered_workspace_kpis
from shared.date_utils import filter_dataframe_by_date


def load_email_data():
    """
    Load and process email data from database.
    
    Returns:
        Tuple of (campaigns_df, leads_df, sequences_df)
    """
    repo = EmailRepository()
    
    with st.spinner("Loading dashboard data..."):
        # Fetch data
        leads_raw = repo.get_leads()
        campaigns_raw = repo.get_campaigns()
        sequences_raw = repo.get_sequences()
        
        # Process data
        leads_df = DataProcessor.process_leads(leads_raw)
        campaigns_df = DataProcessor.process_campaigns(campaigns_raw, leads_df)
        sequences_df = DataProcessor.process_email_sequences(sequences_raw)
    
    return campaigns_df, leads_df, sequences_df


def run_email_dashboard():
    """Main email dashboard rendering function."""
    
    # Title
    st.title("📧 Email Campaign KPI Dashboard")
    
    # Load data once
    campaigns_df, leads_df, sequences_df = load_email_data()
    
    # Navigation State Management
    TABS = ["🏠 Workspace Overview", "🔍 Campaign Analysis"]
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = TABS[0]
    
    def switch_to_analysis():
        """Callback to switch to analysis tab."""
        st.session_state.active_tab = TABS[1]
    
    # Custom CSS for radio button tabs
    st.markdown("""
    <style>
        div[data-testid="stRadio"] > div {
            flex-direction: row;
            gap: 10px;
        }
        div[data-testid="stRadio"] label > div:first-child {
            display: None;
        }
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
        div[data-testid="stRadio"] label:hover {
            border-color: #cbd5e1;
            transform: translateY(-1px);
        }
        div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        div[data-testid="stRadio"] label:has(input:checked) p {
            color: white !important;
            opacity: 1;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Tab Navigation
    # Using st.radio to control the view
    active_tab = st.radio(
        "Navigation",
        TABS,
        key="active_tab",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # --- Sidebar Filters ---
    # We define filters globally here or inside tabs? 
    # To match LinkedIn style, let's keep specific filters in sidebar but with better headers.
    
    with st.sidebar:
        st.divider()
        st.header("🎯 Filters")

    
    if active_tab == TABS[0]:
        # Workspace Overview Tab
        
        # 1. Render Filters (Workspace + Date)
        selected_workspace, start_date, end_date = render_workspace_filters(campaigns_df)
        
        # 2. Render Content
        render_workspace_overview(campaigns_df, leads_df, selected_workspace, start_date, end_date)
        
    elif active_tab == TABS[1]:
        # Campaign Analysis Tab
        
        # 1. Render Workspace Selector (Essential for filtering campaigns)
        # We manually render this part since render_campaign_filters expects a workspace input
        with st.sidebar: 
            workspaces = ["All Workspaces"]
            if not campaigns_df.empty and 'workspace_name' in campaigns_df.columns:
                unique_ws = sorted(campaigns_df['workspace_name'].dropna().unique().tolist())
                workspaces.extend(unique_ws)
            
            selected_workspace = st.selectbox(
                "Select Workspace",
                options=workspaces,
                index=0,
                key="workspace_filter_campaign_tab"
            )
            st.caption(f"Viewing: {selected_workspace}")
            st.divider()

        # 2. Render Campaign & Date Filters
        # Note: render_campaign_filters might also render a "Filters" header.
        selected_campaign, start_date, end_date = render_campaign_filters(
            campaigns_df,
            workspace=selected_workspace,
            on_change=switch_to_analysis
        )
        
        # 3. Render Content
        render_campaign_analysis(
            campaigns_df, leads_df, sequences_df,
            selected_campaign, start_date, end_date
        )



def render_workspace_overview(campaigns_df: pd.DataFrame, leads_df: pd.DataFrame, selected_workspace: str, start_date=None, end_date=None):
    """Render the workspace overview tab."""
    
    # Filter data by workspace
    filtered_campaigns_df = campaigns_df.copy()
    filtered_leads_df = leads_df.copy()
    
    if not campaigns_df.empty:
        if selected_workspace != "All Workspaces":
            filtered_campaigns_df = campaigns_df[campaigns_df['workspace_name'] == selected_workspace]
        
        if not filtered_campaigns_df.empty and 'campaign_id' in filtered_campaigns_df.columns:
            valid_campaign_ids = set(filtered_campaigns_df['campaign_id'].dropna().unique())
            if 'campaign_id' in filtered_leads_df.columns and not filtered_leads_df.empty:
                filtered_leads_df = filtered_leads_df[filtered_leads_df['campaign_id'].isin(valid_campaign_ids)]
    
    # Filter leads by date for activity metrics
    if not filtered_leads_df.empty and 'Date' in filtered_leads_df.columns and start_date and end_date:
         filtered_leads_df = filter_dataframe_by_date(filtered_leads_df, 'Date', start_date, end_date)

    # Calculate and render metrics
    current_metrics = calculate_filtered_workspace_kpis(filtered_campaigns_df, filtered_leads_df)
    render_kpi_cards(current_metrics)
    
    # Charts (using filtered leads for activity charts if applicable, or logic inside charts needs to know context)
    # render_charts usually expects leads_df. If we pass filtered_leads_df, charts will be date-filtered too.
    # This is consistent with "date range filter should also work in workspace overview".
    render_charts(filtered_leads_df, filtered_campaigns_df, key_prefix="workspace")


def render_campaign_analysis(
    campaigns_df: pd.DataFrame,
    leads_df: pd.DataFrame,
    sequences_df: pd.DataFrame,
    selected_campaign: str,
    start_date,
    end_date
):
    """Render the campaign analysis tab."""
    
    if selected_campaign == "No campaigns available" or not selected_campaign:
        st.warning("No campaigns available regarding the filters.")
        return
    
    # Filter campaigns
    campaign_data = campaigns_df[campaigns_df['Name'] == selected_campaign]
    
    if campaign_data.empty:
        st.warning(f"Campaign '{selected_campaign}' not found.")
        return
    
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
    current_metrics = calculate_filtered_kpis(campaign_row, filtered_leads_df)
    
    st.subheader(f"Campaign: {selected_campaign}")
    render_kpi_cards(current_metrics)
    
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
