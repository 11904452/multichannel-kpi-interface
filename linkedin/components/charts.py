import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_lead_status_analysis(leads_df):
    """Render lead status distribution and analysis"""
    if leads_df.empty or 'Status' not in leads_df.columns:
        st.info("No lead status data available")
        return
    
    st.subheader("📊 Lead Status Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Pie chart of status distribution
        status_counts = leads_df['Status'].value_counts()
        
        # Build color map: green for Interested, RdBu palette for rest
        rdbu = px.colors.sequential.RdBu
        other_statuses = [s for s in status_counts.index if s != 'Interested']
        status_color_map = {'Interested': '#059669'}
        for i, s in enumerate(other_statuses):
            status_color_map[s] = rdbu[i % len(rdbu)]

        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Lead Status Distribution",
            hole=0.7,
            color=status_counts.index,
            color_discrete_map=status_color_map
        )
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(
            height=300, 
            margin=dict(l=30, r=30, t=60, b=30),
            title=dict(font=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status metrics
        total_leads = len(leads_df)
        interested = len(leads_df[leads_df['Status'] == 'Interested']) if 'Interested' in leads_df['Status'].values else 0
        not_interested = len(leads_df[leads_df['Status'] == 'Not Interested']) if 'Not Interested' in leads_df['Status'].values else 0
        
        st.metric("Total Leads", f"{total_leads:,}")
        st.metric("Interested Leads", f"{interested:,}", 
                 delta=f"{(interested/total_leads*100):.1f}%" if total_leads > 0 else "0%")
        st.metric("Not Interested", f"{not_interested:,}",
                 delta=f"{(not_interested/total_leads*100):.1f}%" if total_leads > 0 else "0%",
                 delta_color="inverse")

def render_top_accounts(leads_df, accounts_df=None):
    """Render top performing accounts analysis"""
    if leads_df.empty or 'account_name' not in leads_df.columns:
        st.info("No account data available")
        return
    
    st.subheader("🏆 Top Performing Accounts")
    
    # Filter out deleted accounts if accounts_df is provided
    filtered_leads = leads_df.copy()
    if accounts_df is not None and not accounts_df.empty and 'account_id' in accounts_df.columns:
        # Filter accounts where status is NOT 'DELETED'
        active_accounts = accounts_df[accounts_df['status'].str.upper() != 'DELETED']
        active_account_ids = active_accounts['account_id'].astype(str).unique()
        
        # Filter leads to only include those from active accounts
        filtered_leads = filtered_leads[filtered_leads['account_id'].astype(str).isin(active_account_ids)]
        
    if filtered_leads.empty:
        st.info("No active account data available")
        return

    # Aggregate by account
    account_stats = filtered_leads.groupby('account_name').agg({
        'lead_id': 'count',
        'replies': 'sum',
        'Status': lambda x: (x == 'Interested').sum()
    }).reset_index()
    
    account_stats.columns = ['Account', 'Total Leads', 'Total Replies', 'Interested Leads']
    account_stats['Interest Rate %'] = (account_stats['Interested Leads'] / account_stats['Total Leads'] * 100).round(2)
    
    # Deterministic sort: Primary by Interested Leads (desc), Secondary by Account Name (asc) for ties
    account_stats = account_stats.sort_values(by=['Interested Leads', 'Account'], ascending=[False, True])
    
    # Filter controls (outside columns to align start of chart and card)
    f_col1, _ = st.columns([1, 4])
    with f_col1:
        top_n = st.selectbox(
            "Show Top:",
            options=["All", 10],
            index=0, # Default to All
            key="top_accounts_filter"
        )
    
    # Apply filter
    display_stats = account_stats.copy()
    if top_n != "All":
            display_stats = display_stats.head(int(top_n))
    
    # Reverse for horizontal bar chart (so highest is at top)
    display_stats = display_stats.iloc[::-1]

    # Dynamic height based on number of rows
    # Base height 400, add 30px per row.
    # We want it to be substantial.
    row_height = 25
    margin_height = 80
    dynamic_height = max(450, len(display_stats) * row_height + margin_height)

    col1, col2 = st.columns([3, 1]) # Adjusted ratio for better chart width
    
    with col1:
        # Horizontal bar chart
        fig = px.bar(
            display_stats,
            y='Account',
            x='Interested Leads',
            orientation='h',
            title=f"Accounts by Interested Leads ({top_n if top_n != 'All' else 'All'})",
            color='Interest Rate %',
            color_continuous_scale='Viridis',
            text='Interested Leads'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside', marker_line_width=0, marker_cornerradius=8)
        fig.update_layout(
            height=dynamic_height, 
            margin=dict(l=20, r=20, t=50, b=30), 
            yaxis={'categoryorder': 'total ascending'},
            title=dict(font=dict(size=14))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top performer card
        if not account_stats.empty:
            # Use the first record from the deterministically sorted dataframe
            top = account_stats.iloc[0]
            scale = min(1.2, max(0.6, dynamic_height / 450.0))
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        height: {dynamic_height}px;
                        padding: 20px; 
                        border-radius: 10px; 
                        color: white; 
                        text-align: center; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                        display: flex; 
                        flex-direction: column; 
                        justify-content: center;
                        align-items: center;'>
                <div style='font-size: {3 * scale}em; margin-bottom: {10 * scale}px; filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.6)); line-height: 1;'>🥇</div>
                <h3 style='margin:0; color: white; font-size: {2 * scale}em; opacity: 0.9; line-height: 1.1;'>Top Performer</h3>
                <h2 style='margin:-{5 * scale}px 0 {15 * scale}px 0; color: white; font-size: {1.8 * scale}em; line-height: 1.1; word-wrap: break-word; max-width: 100%;'>{top['Account']}</h2>
                <div style='background: rgba(255,255,255,0.2); border-radius: 15px; padding: {15 * scale}px {25 * scale}px; backdrop-filter: blur(5px); width: 100%; box-sizing: border-box;'>
                    <p style='font-size: {2 * scale}em; margin: 0; font-weight: bold; line-height: 1.1;'>{int(top['Interested Leads'])}</p>
                    <p style='font-size: {1 * scale}em; margin: 0; opacity: 0.9;'>Interested Leads</p>
                    <div style='width: 100%; height: 2px; background: rgba(255,255,255,0.3); margin: {8 * scale}px 0;'></div>
                    <p style='font-size: {1.2 * scale}em; margin: 0; font-weight: 200; line-height: 0.7;'>{top['Interest Rate %']:.1f}%</p>
                    <p style='font-size: {1 * scale}em; margin: 0; opacity: 0.8;'>Conversion Rate</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_campaign_effectiveness(campaigns_df, leads_df):
    """Render campaign effectiveness analysis"""
    st.subheader("📈 Campaign Effectiveness")
    
    if campaigns_df.empty:
        st.info("No campaign data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter plot: Acceptance Rate vs Reply Rate
        campaigns_df['acceptance_rate'] = (campaigns_df['accepted_connections'] / campaigns_df['sent_connections'] * 100).fillna(0)
        campaigns_df['reply_rate'] = (campaigns_df['replies'] / campaigns_df['sent_messages'] * 100).fillna(0)
        
        fig = px.scatter(
            campaigns_df,
            x='acceptance_rate',
            y='reply_rate',
            size='sent_connections',
            color='outreach_type',
            hover_data=['campaign_name'],
            title="Campaign Efficiency Matrix",
            labels={'acceptance_rate': 'Acceptance Rate (%)', 'reply_rate': 'Reply Rate (%)'}
        )
        fig.update_layout(
            height=300, 
            margin=dict(l=20, r=20, t=60, b=20),
            title=dict(font=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Outreach type comparison
        if 'outreach_type' in campaigns_df.columns:
            outreach_stats = campaigns_df.groupby('outreach_type').agg({
                'sent_connections': 'sum',
                'accepted_connections': 'sum',
                'replies': 'sum'
            }).reset_index()
            
            outreach_stats['acceptance_rate'] = (outreach_stats['accepted_connections'] / outreach_stats['sent_connections'] * 100).round(2)
            outreach_stats['reply_rate'] = (outreach_stats['replies'] / outreach_stats['sent_connections'] * 100).round(2)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Acceptance Rate',
                x=outreach_stats['outreach_type'],
                y=outreach_stats['acceptance_rate'],
                marker_color='#667eea'
            ))
            fig.add_trace(go.Bar(
                name='Reply Rate',
                x=outreach_stats['outreach_type'],
                y=outreach_stats['reply_rate'],
                marker_color='#764ba2'
            ))
            
            fig.update_layout(
                title="Performance by Outreach Type",
                barmode='group',
                height=300,
                margin=dict(l=20, r=20, t=60, b=20),
                yaxis_title="Rate (%)",
                title_font=dict(size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

def map_job_title_to_seniority(title):
    """Map job title to seniority level"""
    if not isinstance(title, str):
        return "Entry Level"
    
    title_lower = title.lower()
    
    # Define keywords for each level (Order matters: higher seniority first)
    has_owner = any(x in title_lower for x in ['owner', 'founder', 'co-founder', 'partner', 'principal'])
    has_cxo = any(x in title_lower for x in ['chief', 'c-suite', 'ceo', 'cto', 'cfo', 'coo', 'cmo', 'president', 'executive'])
    has_vp = any(x in title_lower for x in ['vp', 'vice president'])
    has_director = any(x in title_lower for x in ['director', 'head'])
    has_manager = any(x in title_lower for x in ['manager', 'lead', 'supervisor'])
    
    if has_owner: return "Owner"
    if has_cxo: return "CXO"
    if has_vp: return "VP"
    if has_director: return "Director"
    if has_manager: return "Manager"
    
    return "Entry Level"

def render_seniority_level_analysis(leads_df):
    """Render seniority level analysis using the 'Seniority' column from replied leads."""

    # Require the direct Seniority column; fall back to job_title mapping if absent
    has_seniority_col = 'Seniority' in leads_df.columns
    has_job_title_col = 'job_title' in leads_df.columns

    if leads_df.empty or (not has_seniority_col and not has_job_title_col):
        return

    st.subheader("💼 Seniority Level Insights")

    df_analysis = leads_df.copy()

    if has_seniority_col:
        # Primary path: use the Seniority column directly
        df_analysis['_seniority'] = (
            df_analysis['Seniority']
            .fillna('Unknown')
            .astype(str)
            .str.strip()
            .replace('', 'Unknown')
        )
    else:
        # Fallback: derive from job_title keywords
        df_analysis['_seniority'] = df_analysis['job_title'].apply(map_job_title_to_seniority)

    # Drop rows with no meaningful seniority
    df_analysis = df_analysis[df_analysis['_seniority'].str.lower() != 'unknown']

    if df_analysis.empty:
        st.info("No seniority data available for replied leads.")
        return

    # Aggregate stats by Seniority
    seniority_stats = df_analysis.groupby('_seniority').agg(
        Total_Leads=('lead_id', 'count'),
        Interested=('Status', lambda x: (x == 'Interested').sum())
    ).reset_index()

    seniority_stats.columns = ['Seniority Level', 'Total Leads', 'Interested']
    seniority_stats['Interest Rate %'] = (
        seniority_stats['Interested'] / seniority_stats['Total Leads'] * 100
    ).round(2)

    # Sort by Interest Rate for the chart
    seniority_stats = seniority_stats.sort_values('Interest Rate %', ascending=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            seniority_stats,
            x='Interest Rate %',
            y='Seniority Level',
            orientation='h',
            title="Interest Rate by Seniority Level",
            color='Total Leads',
            color_continuous_scale='Blues',
            text='Interest Rate %'
        )
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            marker_line_width=0,
            marker_cornerradius=8
        )
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=60, b=20),
            title=dict(font=dict(size=14))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Key Insights")

        top_stats = seniority_stats.sort_values('Interest Rate %', ascending=False)

        if not top_stats.empty:
            best_level = top_stats.iloc[0]
            st.markdown(f"""
            **Most Responsive Level:**  
            {best_level['Seniority Level']}  
            *{best_level['Interest Rate %']:.1f}% interest rate*
            """)

        st.markdown("**Distribution:**")
        dist = df_analysis['_seniority'].value_counts(normalize=True) * 100
        for level, pct in dist.head(5).items():
            st.markdown(f"- {level}: {pct:.1f}%")

def render_analytics_section(leads_df):
    """Render advanced analytics section with dynamic chart"""
    if leads_df.empty or 'reply_date' not in leads_df.columns:
        return
    
    # Section Header
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="margin: 0;">📈 Analytics</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Filter out null dates and ensure datetime
    timeline_df = leads_df[leads_df['reply_date'].notna()].copy()
    if timeline_df.empty:
        st.info("No timeline data available")
        return
        
    timeline_df['date'] = pd.to_datetime(timeline_df['reply_date']).dt.date
    
    # --- Data Processing for All Metrics ---
    # Group by date and calculate counts for each metric
    daily_data = timeline_df.groupby('date').agg({
        'lead_id': 'count', # Total Replies
        'Status': [
            lambda x: (x == 'Interested').sum(),
            lambda x: (x == 'Not Interested').sum(),
            lambda x: x.isin(['Objection', 'Objections']).sum(),
            lambda x: x.astype(str).str.contains('Revisit', case=False, na=False).sum()
        ]
    }).reset_index()
    
    # Flatten MultiIndex columns
    daily_data.columns = ['Date', 'Replies', 'Interested', 'Not Interested', 'Objection', 'Revisit Later']
    
    # Ensure all dates in range are present (fill gaps with 0)
    min_date = daily_data['Date'].min()
    max_date = daily_data['Date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D').date
    
    daily_data = daily_data.set_index('Date').reindex(all_dates, fill_value=0).reset_index()
    daily_data.rename(columns={'index': 'Date'}, inplace=True)

    # --- Metric Selection UI ---
    # mapping friendly names to column names and colors
    metrics_config = {
        "Replies": {"col": "Replies", "color": "#6366f1", "icon": "↩️"},
        "Interested": {"col": "Interested", "color": "#10b981", "icon": "✅"},
        "Not Interested": {"col": "Not Interested", "color": "#ef4444", "icon": "🚫"},
        "Objection": {"col": "Objection", "color": "#f59e0b", "icon": "⚠️"},
        "Revisit Later": {"col": "Revisit Later", "color": "#8b5cf6", "icon": "⏳"}
    }
    
    # Custom CSS for the metric selector to look like tabs
    st.markdown("""
    <style>
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 5px;
    }
    div[data-testid="stRadio"] label {
        background-color: #f1f5f9;
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
        font-weight: 500;
        font-size: 0.9rem;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #e2e8f0;
        border-color: #cbd5e1;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background-color: #f8fafc; /* light background */
        border-color: #6366f1; /* primary border */
        color: #6366f1;
        font-weight: 600;
        box-shadow: 0 0 0 1px #6366f1;
    }
    div[data-testid="stRadio"] label:has(input:checked) div {
        color: #6366f1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    selected_metric_name = st.radio(
        "Select Metric",
        options=list(metrics_config.keys()),
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="analytics_metric_selector"
    )
    
    # Get config for selected metric
    config = metrics_config[selected_metric_name]
    col_name = config['col']
    chart_color = config['color']
    
    # Calculate Summary Stats for the selected metric
    total_count = daily_data[col_name].sum()
    
    # --- Render Chart Section ---
    # Container styling
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.05);">
        <div style="margin-bottom: 20px;">
             <span style="font-size: 0.9rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">{config['icon']} {selected_metric_name}</span>
             <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b; line-height: 1.2;">+{total_count}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Plotly Chart
    fig = go.Figure()
    
    # Add Gradient Area Trace
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data[col_name],
        mode='lines',
        name=selected_metric_name,
        line=dict(color=chart_color, width=3, shape='spline', smoothing=1.3),
        fill='tozeroy',
        # Create a gradient effect using rgba
        fillcolor=f"rgba({int(chart_color[1:3], 16)}, {int(chart_color[3:5], 16)}, {int(chart_color[5:7], 16)}, 0.1)" 
    ))
    
    # Add Markers for non-zero points only to keep it clean, or just hover points
    # Let's add specific markers for the checked point style
    fig.add_trace(go.Scatter(
        x=daily_data['Date'],
        y=daily_data[col_name],
        mode='markers',
        marker=dict(
            size=8,
            color='white',
            line=dict(color=chart_color, width=2)
        ),
        showlegend=False,
        hoverinfo='skip' # The line trace handles hover better
    ))

    # Layout Updates for "High Tech" / Clean Look
    fig.update_layout(
        template='plotly_white',
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickformat="%b %d",
            tickfont=dict(color='#94a3b8', size=11),
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f1f5f9',
            gridwidth=1,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(color='#94a3b8', size=11),
            fixedrange=True
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='white',
            font_size=13,
            font_family="Inter, sans-serif",
            bordercolor=chart_color
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_conversion_funnel(campaigns_df: pd.DataFrame, leads_df: pd.DataFrame):
    """Render conversion funnel chart"""
    
    st.markdown("### 🎯 Conversion Funnel")
    
    if campaigns_df.empty:
        st.info("No campaign data available")
        return
    
    total_sent = campaigns_df['sent_connections'].sum()
    total_accepted = campaigns_df['accepted_connections'].sum()
    
    # Count replied leads: where replies is not null and > 0
    from linkedin.services.metrics import count_replied_leads, get_replied_leads
    total_replies = count_replied_leads(leads_df)
    
    # Get replied leads and count interested
    replied_leads_df = get_replied_leads(leads_df)
    interested = 0
    if not replied_leads_df.empty and 'Status' in replied_leads_df.columns:
        interested = len(replied_leads_df[replied_leads_df['Status'] == 'Interested'])
    
    funnel_data = pd.DataFrame({
        'Stage': ['Sent', 'Accepted', 'Replied', 'Interested'],
        'Count': [total_sent, total_accepted, total_replies, interested]
    })
    
    fig = px.funnel(
        funnel_data,
        x='Count',
        y='Stage',
        title="Complete Conversion Funnel"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

@st.dialog("⚠️ Confirm Deletion")
def confirm_delete_dialog(campaign_id: str, campaign_name: str, index: int):
    """Dialog to confirm campaign deletion"""
    st.markdown(f"""
        <div style="background-color: #fff3cd; 
                    border: 1px solid #ffeeba; 
                    border-radius: 8px; 
                    padding: 16px; 
                    margin-bottom: 20px;">
            <p style="color: #856404; margin: 0; font-size: 16px;">
                Are you sure you want to delete campaign <strong>"{campaign_name}"</strong>?
            </p>
            <p style="color: #856404; margin: 8px 0 0 0; font-size: 14px;">
                This action cannot be undone and will remove all associated data from the database.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Yes, Delete", key=f"confirm_del_{campaign_id}_{index}", type="primary", use_container_width=True):
            # Use the LinkedInCampaignAPI
            from api.linkedin_api import LinkedInCampaignAPI
            api = LinkedInCampaignAPI()
            
            with st.spinner("Deleting campaign..."):
                response = api.delete_campaign(str(campaign_id))
            
            # Handle case where response might be a string (based on user edits/testing)
            if isinstance(response, str):
                st.session_state['delete_success'] = response
                st.rerun()
                
            elif isinstance(response, dict) and response.get('success', False):
                # Store success message from API
                st.session_state['delete_success'] = response.get('message', 'Campaign deleted successfully')
                st.rerun()
            else:
                # Handle error
                error_message = response.get('message', 'Failed to delete campaign') if isinstance(response, dict) else str(response)
                st.session_state['delete_error'] = error_message
                st.rerun()
    
    with col2:
        if st.button("❌ Cancel", key=f"cancel_del_{campaign_id}_{index}", use_container_width=True):
            st.rerun()

def render_detailed_tables(campaigns_df: pd.DataFrame, leads_df: pd.DataFrame):
    """Render detailed data tables with enhanced styling"""
    st.subheader("📋 Detailed Data Tables")
    
    # Custom CSS for styling the Delete button and Status
    # We target buttons inside columns that are NOT disabled. 
    # This should affect the delete buttons in the table but not the download button (which is outside columns).
    st.markdown("""
        <style>
        /* Style for enabled delete buttons (soft red theme) */
        div[data-testid="column"] button:not([disabled]) {
            background-color: #ffebee !important;
            color: #ef5350 !important;
            border-color: #ffcdd2 !important;
        }
        div[data-testid="column"] button:not([disabled]):hover {
            background-color: #ffcdd2 !important;
            color: #d32f2f !important;
            border-color: #ef5350 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Campaign Details", "Lead Details"])
    
    with tab1:
        if not campaigns_df.empty:
            # --- Pre-compute per-campaign stats from leads_df ---
            if not leads_df.empty and 'campaign_id' in leads_df.columns:
                # Total leads per campaign (row count)
                lead_counts = leads_df.groupby('campaign_id').size().rename('total_leads')
                # Interested leads per campaign
                interested_counts = (
                    leads_df[leads_df['Status'] == 'Interested']
                    .groupby('campaign_id').size()
                    .rename('interested_count')
                )
            else:
                lead_counts = pd.Series(dtype=int, name='total_leads')
                interested_counts = pd.Series(dtype=int, name='interested_count')

            # Download Button
            csv = campaigns_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="linkedin_campaigns.csv",
                mime="text/csv",
                key="download_campaigns"
            )

            # Table Header
            h1, h2, h3, h4, h5, h6, h7, h8, h9, h10 = st.columns(
                [2.5, 1.3, 1, 0.8, 0.8, 0.85, 0.9, 0.7, 0.8, 0.6]
            )
            header_style = "<span style='color: #1e293b; font-weight: 700;'>"
            h1.markdown(f"{header_style}Campaign</span>", unsafe_allow_html=True)
            h2.markdown(f"{header_style}Workspace</span>", unsafe_allow_html=True)
            h3.markdown(f"{header_style}Status</span>", unsafe_allow_html=True)
            h4.markdown(f"{header_style}Sent</span>", unsafe_allow_html=True)
            h5.markdown(f"{header_style}Acc.%</span>", unsafe_allow_html=True)
            h6.markdown(f"{header_style}Reply%</span>", unsafe_allow_html=True)
            h7.markdown(f"{header_style}Interested %</span>", unsafe_allow_html=True)
            h8.markdown(f"{header_style}Leads</span>", unsafe_allow_html=True)
            h9.markdown(f"{header_style}Complete</span>", unsafe_allow_html=True)
            h10.markdown(f"{header_style}Action</span>", unsafe_allow_html=True)

            st.divider()

            # Table Rows
            for index, row in campaigns_df.iterrows():
                c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(
                    [2.5, 1.3, 1, 0.8, 0.8, 0.85, 0.9, 0.7, 0.8, 0.6]
                )
                campaign_id = row.get('campaign_id')

                with c1:
                    st.write(row.get('campaign_name', ''))

                with c2:
                    st.write(row.get('workspace_name', ''))

                with c3:
                    status = row.get('Status', '')
                    is_deleted = str(status).lower() == 'deleted' if status else False
                    if is_deleted:
                        st.markdown(
                            f"<span style='color: #ef5350; font-weight: 600;'>{status}</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.write(status)

                with c4:
                    st.write(f"{int(row.get('sent_connections', 0))}")

                with c5:
                    sent = row.get('sent_connections', 0) or 0
                    accepted = row.get('accepted_connections', 0) or 0
                    acc_rate = (accepted / sent * 100) if sent > 0 else 0
                    st.write(f"{acc_rate:.1f}%")

                with c6:
                    replies = row.get('replies', 0) or 0
                    sent_msgs = row.get('sent_messages', 0) or 0
                    rr = (replies / sent_msgs * 100) if sent_msgs > 0 else 0
                    st.write(f"{rr:.1f}% ({int(replies)})")

                with c7:
                    int_count = int(interested_counts.get(campaign_id, 0)) if campaign_id in interested_counts.index else 0
                    int_rate = (int_count / replies * 100) if replies > 0 else 0
                    st.write(f"{int_rate:.1f}% ({int_count})")

                with c8:
                    total_leads_count = int(lead_counts.get(campaign_id, 0)) if campaign_id in lead_counts.index else 0
                    st.write(f"{total_leads_count}")

                with c9:
                    st.write(f"{int(row.get('complete', 0))}")

                with c10:
                    campaign_name = row.get('campaign_name', 'Campaign')
                    if st.button("🗑️", key=f"del_{campaign_id}_{index}", disabled=not is_deleted, help="Delete Campaign"):
                        confirm_delete_dialog(campaign_id, campaign_name, index)

                st.divider()
    with tab2:
        if not leads_df.empty:
            
            # Download Button for Leads
            csv_leads = leads_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv_leads,
                file_name="linkedin_leads.csv",
                mime="text/csv",
                key="download_leads"
            )

            display_cols = [
                'name', 'job_title', 'Status', 'account_name', 
                'replies', 'reply_date', 'type', 'inmail', 'automated'
            ]
            cols = [c for c in display_cols if c in leads_df.columns]
            
            st.dataframe(
                leads_df[cols],
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn("Lead Name", width="medium"),
                    "job_title": st.column_config.TextColumn("Job Title", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "reply_date": st.column_config.DatetimeColumn("Reply Date", format="D MMM YYYY"),
                    "account_name": st.column_config.TextColumn("Account Name", width="medium")
                }
            )
