import streamlit as st
from datetime import datetime
from typing import Tuple, List, Optional
from shared.date_utils import get_date_range
import pandas as pd

def render_filters(campaigns_df: pd.DataFrame) -> Tuple[str, datetime, datetime, List[str]]:
    """
    Render sidebar filters and return selected values.
    
    Returns:
        Tuple of (selected_workspace, start_date, end_date, selected_campaigns)
    """
    with st.sidebar:
        st.header("Filters")
        
        # extraction unique workspaces
        workspaces = ["All Workspaces"]
        if not campaigns_df.empty and 'workspace_name' in campaigns_df.columns:
            unique_ws = sorted(campaigns_df['workspace_name'].dropna().unique().tolist())
            workspaces.extend(unique_ws)
        
        # 1. Workspace Filter
        selected_workspace = st.selectbox(
            "Select Workspace",
            options=workspaces,
            index=0
        )
        
        # 2. Date Range Filter
        date_options = [
            "Today",
            "This Week",
            "Last Week",
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month",
            "All Time",
            "Custom Date Range"
        ]
        
        selected_date_filter = st.selectbox(
            "Date Range",
            options=date_options,
            index=3  # Default: Last 7 Days
        )
        
        custom_start, custom_end = None, None
        if selected_date_filter == "Custom Date Range":
            custom_start = st.date_input("📅 Start Date", datetime.now().date())
            custom_start = datetime.combine(custom_start, datetime.min.time())
            custom_end = st.date_input("📅 End Date", datetime.now().date())
            custom_end = datetime.combine(custom_end, datetime.max.time())
                
        start_date, end_date = get_date_range(selected_date_filter, custom_start, custom_end)
        
        # 3. Campaign Name Filter
        available_campaigns = []
        if not campaigns_df.empty and 'Name' in campaigns_df.columns:
            # Filter by workspace if selected
            if selected_workspace != "All Workspaces":
                filtered_df = campaigns_df[campaigns_df['workspace_name'] == selected_workspace]
                available_campaigns = sorted(filtered_df['Name'].dropna().unique().tolist())
            else:
                available_campaigns = sorted(campaigns_df['Name'].dropna().unique().tolist())
            
        selected_campaigns = st.multiselect(
            "Select Campaigns",
            options=available_campaigns,
            default=[]
        )
        
        # Display active filters summary
        st.divider()
        st.caption(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        return selected_workspace, start_date, end_date, selected_campaigns

def render_workspace_filters(campaigns_df: pd.DataFrame) -> str:
    """
    Render workspace filter only for workspace overview tab.
    
    Returns:
        Tuple of (selected_workspace, start_date, end_date)
    """
    with st.sidebar:

        
        # Extract unique workspaces
        workspaces = ["All Workspaces"]
        if not campaigns_df.empty and 'workspace_name' in campaigns_df.columns:
            unique_ws = sorted(campaigns_df['workspace_name'].dropna().unique().tolist())
            workspaces.extend(unique_ws)
        
        # Workspace Filter
        selected_workspace = st.selectbox(
            "Select Workspace",
            options=workspaces,
            index=0,
            key="workspace_filter"
        )
        
        # Date Range Filter
        date_options = [
            "Today",
            "This Week",
            "Last Week",
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month",
            "All Time",
            "Custom Date Range"
        ]
        
        selected_date_filter = st.selectbox(
            "Date Range",
            options=date_options,
            index=3,  # Default: Last 7 Days
            key="workspace_date_filter"
        )
        
        custom_start, custom_end = None, None
        if selected_date_filter == "Custom Date Range":
            custom_start = st.date_input("📅 Start Date", datetime.now().date(), key="ws_custom_start")
            custom_start = datetime.combine(custom_start, datetime.min.time())
            custom_end = st.date_input("📅 End Date", datetime.now().date(), key="ws_custom_end")
            custom_end = datetime.combine(custom_end, datetime.max.time())
                
        start_date, end_date = get_date_range(selected_date_filter, custom_start, custom_end)

        st.divider()
        st.caption(f"Viewing: {selected_workspace}")
        st.caption(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        return selected_workspace, start_date, end_date

def render_campaign_filters(campaigns_df: pd.DataFrame, workspace: Optional[str] = None, on_change: Optional[callable] = None) -> Tuple[str, datetime, datetime]:
    """
    Render campaign selector and date range filter for campaign analysis tab.
    
    Args:
        campaigns_df: DataFrame containing campaign data
        workspace: Optional workspace filter to apply
        on_change: Callback function to trigger when campaign is selected
    
    Returns:
        Tuple of (selected_campaign, start_date, end_date)
    """
    with st.sidebar:

        
        # Filter campaigns by workspace if provided
        filtered_campaigns_df = campaigns_df
        if workspace and workspace != "All Workspaces" and not campaigns_df.empty:
            filtered_campaigns_df = campaigns_df[campaigns_df['workspace_name'] == workspace]
        
        # Campaign selector
        available_campaigns = []
        if not filtered_campaigns_df.empty and 'Name' in filtered_campaigns_df.columns:
            available_campaigns = sorted(filtered_campaigns_df['Name'].dropna().unique().tolist())
        
        # Validate current selection against available options to prevent KeyErrors
        if "campaign_filter" in st.session_state:
            current_selection = st.session_state.campaign_filter
            # If current selection is not in available campaigns (and we have campaigns), reset it
            if available_campaigns and current_selection not in available_campaigns:
                # Reset to first available or clear if needed. 
                # Streamlit's default behavior with index=0 will handle the new default 
                # if we just remove the invalid entry or let it update.
                # However, explicit setting is safer for immediate consistency.
                st.session_state.campaign_filter = available_campaigns[0]
            elif not available_campaigns:
                 # If no campaigns, maybe clear it?
                 pass

        selected_campaign = st.selectbox(
            "Select Campaign",
            options=available_campaigns if available_campaigns else ["No campaigns available"],
            index=0,
            key="campaign_filter",
            on_change=on_change if on_change else None
        )
        
        # Date Range Filter
        date_options = [
            "Today",
            "This Week",
            "Last Week",
            "Last 7 Days",
            "Last 30 Days",
            "This Month",
            "Last Month",
            "All Time",
            "Custom Date Range"
        ]
        
        selected_date_filter = st.selectbox(
            "Date Range",
            options=date_options,
            index=3,  # Default: Last 7 Days
            key="date_filter"
        )
        
        custom_start, custom_end = None, None
        if selected_date_filter == "Custom Date Range":
            custom_start = st.date_input("📅 Start Date", datetime.now().date(), key="start_date")
            custom_start = datetime.combine(custom_start, datetime.min.time())
            custom_end = st.date_input("📅 End Date", datetime.now().date(), key="end_date")
            custom_end = datetime.combine(custom_end, datetime.max.time())
                
        start_date, end_date = get_date_range(selected_date_filter, custom_start, custom_end)
        
        # Display active filters summary
        st.divider()
        st.caption(f"Campaign: {selected_campaign}")
        st.caption(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        return selected_campaign, start_date, end_date

