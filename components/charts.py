import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import numpy as np
# Define calm pastel palette
PASTEL_PALETTE = [
    '#88B3C8', # Blue
    '#FFB7B2', # Red/Pink
    '#B5EAD7', # Green
    '#E2F0CB', # Lime
    '#FFDAC1', # Peach
    '#E0BBE4', # Purple
    '#957DAD', # Darker Purple
    '#D291BC', # Magenta
    '#FEC8D8', # Light Pink
    '#FFDFD3'  # Light Orange
]
SOFT_MUTED_PALETTE = [
    "#AFC6D6",  # Soft steel blue
    "#BFD7EA",  # Light powder blue
    "#C9E4DE",  # Muted aqua
    "#D8E2DC",  # Soft sage
    "#EAD7C3",  # Warm sand
    "#E6CDE3",  # Muted lavender
    "#D9C6D5",  # Soft mauve
    "#E8D6DC",  # Dusty rose
    "#F0DEE5",  # Very light blush
    "#F4E6DC",  # Pale peach
]

def update_chart_layout(fig, title="", show_legend=True):
    """Helper to apply consistent calm styling to all charts"""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=15, color="#334155", family="Inter, sans-serif"),
            x=0,
            xanchor='left',
            y=0.98,
            yanchor='top',
            pad=dict(b=9)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="sans-serif", color="#6E6E6E"),
        showlegend=show_legend,
        margin=dict(l=30, r=30, t=60, b=30),
        colorway=SOFT_MUTED_PALETTE,
        height=350
    )
    return fig

def render_charts(leads_df: pd.DataFrame, campaigns_df: pd.DataFrame, key_prefix: str = "default"):
    """
    Render all dashboard charts separated by sections.
    """
    
    # --- Section 2: Reply Analysis ---
    st.subheader("Reply Analysis")
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if not leads_df.empty:
            # Calculate total leads
            if not campaigns_df.empty and 'leads_contacted' in campaigns_df.columns:
                total_leads = pd.to_numeric(campaigns_df['leads_contacted'], errors='coerce').fillna(0).sum()
            else:
                # Fallback if columns missing
                total_leads = len(leads_df)
            
            # Calculate reply counts
            # human_replies = leads_df[leads_df['is_human_reply'] == 1].shape[0]
            human_replies = leads_df['is_human_reply'].fillna(0).sum()
            total_replies = leads_df[leads_df['unique_replies'] > 0].shape[0]
            
            # Calculate reply rates as percentages
            human_reply_rate = (human_replies / total_leads * 100) if total_leads > 0 else 0
            overall_reply_rate = (total_replies / total_leads * 100) if total_leads > 0 else 0
            
            # Prepare data
            data = pd.DataFrame({
                'Type': ['Human Reply Rate', 'Overall Reply Rate'],
                'Rate': [f"{human_reply_rate:.2f}", f"{overall_reply_rate:.2f}"]
            })
            
            fig = px.bar(
                data, 
                x='Rate', 
                y='Type', 
                orientation='h',
                text='Rate', # Removed to hide text
                color='Type',
                color_discrete_sequence=SOFT_MUTED_PALETTE
            )
            update_chart_layout(fig, title='Overall Reply Metrics', show_legend=False)
            # Add styling: width for slimness, marker line, rounded corners
            fig.update_traces(
                width=0.5, 
                marker_line_width=0.3, # Clean look
                marker_cornerradius=10, # Rounded edges
                hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
            )
            
            fig.update_yaxes(title=None)
            fig.update_xaxes(title='Reply Rate (%)', showgrid=False)
            st.plotly_chart(fig, width='stretch')
            
    with col2:
        if not leads_df.empty:
            # Reply Type Breakdown (Status)
            status_counts = leads_df['status'].value_counts()
            interested_stats = ['Interested', 'Not Interested', 'Objections', 'Automated Reply', 'Revisit Later','Bounced']
            filtered_counts = status_counts[status_counts.index.isin(interested_stats)]
            
            if not filtered_counts.empty:
                data = pd.DataFrame({
                    'Status': filtered_counts.index,
                    'Count': filtered_counts.values
                })
                
                fig = px.bar(
                    data,
                    x='Count',
                    y='Status',
                    orientation='h',
                    # text='Count', # Removed
                    color='Status',
                    color_discrete_sequence=SOFT_MUTED_PALETTE
                )
                update_chart_layout(fig, title='Reply Type Breakdown', show_legend=False)
                fig.update_traces(
                    width=0.5, 
                    marker_line_width=0.3,
                    marker_cornerradius=10, # Rounded edges
                    hovertemplate='%{y}: %{x}<extra></extra>'
                )
                fig.update_yaxes(title=None)
                fig.update_xaxes(title=None, showgrid=False)
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No reply status data available.")

    # Bounce & ESP Analysis
    st.markdown("")

    if key_prefix == "campaign":
        # Campaign Analysis: 3 columns (Bounce, Sender ESP, Lead ESP)
        col_bounce, col_sender, col_lead = st.columns(3, gap="large")
        col4_container = None # Hide Top 10 Campaigns
    else:
        # Workspace Analysis: 2 Rows of 2 columns
        # Row 1
        col_bounce, col4_container = st.columns(2, gap="large")
        # Row 2 (will be created later for ESP)
        col_sender = None 
        col_lead = None

    # 1. Bounce Type Distribution (Rendered in col_bounce)
    with col_bounce:
        if not leads_df.empty:
            # Filter out null/empty bounce types
            valid_bounces = leads_df[
                (leads_df['bounce_type'].notna()) & 
                (leads_df['bounce_type'] != '') & 
                (leads_df['bounce_type'] != 'None') & 
                (leads_df['bounce_type'] != 'nan')
            ]
            bounce_counts = valid_bounces['bounce_type'].value_counts()
            
            if not bounce_counts.empty:
                fig = px.pie(
                    values=bounce_counts.values,
                    names=bounce_counts.index,
                    color_discrete_sequence=SOFT_MUTED_PALETTE,
                    hole=0.6
                )
                update_chart_layout(fig, title='Bounce Type Distribution')
                # White borders and percent only inside
                fig.update_traces(
                    textposition='inside', 
                    textinfo='percent',
                    marker=dict(line=dict(color='#ffffff', width=2))
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No bounce data available.")
                
    # 2. Top 10 Campaigns (Rendered in col4_container if it exists)
    if col4_container:
        with col4_container:
            if not campaigns_df.empty:
                # Bounce Rate by Campaign
                if 'bounce_rate' not in campaigns_df.columns:
                    campaigns_df['bounce_rate'] = (campaigns_df['bounced'] / campaigns_df['emails_sent'] * 100).fillna(0)
                
                # Filter non-zero bounce rates or just top 10
                top_bounce_campaigns = campaigns_df.sort_values('bounce_rate', ascending=False).head(10)
                
                fig = px.bar(
                    top_bounce_campaigns,
                    x='Name',
                    y='bounce_rate',
                    text='bounce_rate',
                    labels={'Name': 'Campaign', 'bounce_rate': 'Bounce Rate (%)'},
                    hover_data=['bounced'],
                    color='Name',
                    color_discrete_sequence=SOFT_MUTED_PALETTE
                )
                update_chart_layout(fig, title='Top 10 Campaigns by Bounce Rate', show_legend=False)
                fig.update_traces(
                    texttemplate='%{text:.2f}%', 
                    textposition='inside',
                    marker_line_width=0.3,
                    marker_cornerradius=10 # Rounded
                )
                fig.update_xaxes(title=None, showgrid=False)
                fig.update_yaxes(title='Bounce Rate %', showgrid=True, gridcolor='rgba(0,0,0,0.05)')
                st.plotly_chart(fig, width='stretch')

    # ESP Analysis Setup
    if key_prefix != "campaign":
        # If not campaign mode, create the new row for ESP analysis
        st.markdown("")
        col_sender, col_lead = st.columns(2, gap="large")

    # 3. Sender ESP Distribution (Rendered in col_sender)
    if col_sender:
        with col_sender:
            if not leads_df.empty and 'sender_inbox_esp' in leads_df.columns:
                esp_counts = leads_df['sender_inbox_esp'].value_counts()
                if not esp_counts.empty:
                    fig = px.pie(
                        values=esp_counts.values,
                        names=esp_counts.index,
                        color_discrete_sequence=PASTEL_PALETTE,
                        hole=0.6
                    )
                    update_chart_layout(fig, title='Sender ESP Distribution')
                    # White borders and percent only
                    fig.update_traces(
                        textposition='inside', 
                        textinfo='percent',
                        marker=dict(line=dict(color='#ffffff', width=2))
                    )
                    st.plotly_chart(fig, width='stretch')
                
    # 4. Lead ESP Distribution (Rendered in col_lead)
    if col_lead:
        with col_lead:
            if not leads_df.empty and 'lead_esp' in leads_df.columns:
                lead_esp_counts = leads_df['lead_esp'].value_counts()
                if not lead_esp_counts.empty:
                    fig = px.pie(
                        values=lead_esp_counts.values,
                        names=lead_esp_counts.index,
                        color_discrete_sequence=PASTEL_PALETTE,
                        hole=0.6
                    )
                    update_chart_layout(fig, title='Lead ESP Distribution')
                    # White borders and percent only
                    fig.update_traces(
                        textposition='inside', 
                        textinfo='percent',
                        marker=dict(line=dict(color='#ffffff', width=2))
                    )
                    st.plotly_chart(fig, width='stretch')
                
    # --- ESP Performance Matrix ---
    if not leads_df.empty and 'sender_inbox_esp' in leads_df.columns and 'lead_esp' in leads_df.columns:
        st.write("")
        st.write("")
        st.subheader("ESP Performance Matrix")
        
        # Prepare data for pivot tables
        df_pivot = leads_df.copy()
        
        # Calculate leads contacted based on unique sender_inbox_esp count
        if df_pivot['sender_inbox_esp'].nunique() == 1:
            # Case 1: Single ESP - take from campaigns_df
            if not campaigns_df.empty and 'leads_contacted' in campaigns_df.columns:
                 total_leads_contacted = pd.to_numeric(campaigns_df['leads_contacted'], errors='coerce').fillna(0).sum()
            else:
                 total_leads_contacted = len(df_pivot)
        else:
            # Case 2: Broad Analysis - take from leads_df specific to sender_inbox_esp
            # We return a Series indexed by sender_inbox_esp
            total_leads_contacted = df_pivot.groupby('sender_inbox_esp')['lead_id'].count()
            # Add Total for margins
            total_leads_contacted['Total'] = total_leads_contacted.sum()
             
        # Ensure numeric for aggregation
        df_pivot['is_reply_bool'] = pd.to_numeric(df_pivot['unique_replies'], errors='coerce').fillna(0) > 0
        df_pivot['is_human_reply_bool'] = pd.to_numeric(df_pivot['is_human_reply'], errors='coerce').fillna(0) > 0
        
        st.markdown("**Total Reply Rate by Lead ESP & Inbox ESP**")
        
        # Check if we have data (handle both scalar and Series)
        has_data = False
        if isinstance(total_leads_contacted, (int, float, np.number)):
             has_data = total_leads_contacted > 0
        else:
             has_data = total_leads_contacted.sum() > 0 if not total_leads_contacted.empty else False

        if has_data:
            # Create pivot table with margins (sums of replies)
            pivot_total = pd.pivot_table(
                df_pivot, 
                values='is_reply_bool', 
                index='sender_inbox_esp', 
                columns='lead_esp', 
                aggfunc='sum',
                margins=True,
                margins_name='Total'
            )
            
            # Calculate percentage based on TOTAL leads contacted
            # Replace NaNs with 0 before calculation
            pivot_total = pivot_total.fillna(0)
            
            if isinstance(total_leads_contacted, (int, float, np.number)):
                 pivot_total = (pivot_total / total_leads_contacted) * 100
            else:
                 pivot_total = pivot_total.div(total_leads_contacted, axis=0) * 100
        else:
            pivot_total = pd.DataFrame()

        # Setup column config for dynamic columns
        column_config = {
            col: st.column_config.NumberColumn(format="%.2f%%") 
            for col in pivot_total.columns
        }
            
        st.dataframe(
            pivot_total,
            column_config=column_config,
            width='stretch'
        )

    if not leads_df.empty and 'sender_inbox_esp' in leads_df.columns and 'lead_esp' in leads_df.columns:
        st.write("")
        st.write("")
        st.subheader("Human Reply Rate by Lead ESP & Inbox ESP")

        # Reuse df_pivot and total_leads_contacted from above block
                
        st.markdown("**Human Reply Rate by Lead ESP & Inbox ESP**")
        
        if has_data:
            # Create pivot table with margins (sums of human replies)
            pivot_human = pd.pivot_table(
                df_pivot, 
                values='is_human_reply_bool', 
                index='sender_inbox_esp', 
                columns='lead_esp', 
                aggfunc='sum',
                margins=True,
                margins_name='Total'
            )
            
            # Convert to percentage of TOTAL leads
            pivot_human = pivot_human.fillna(0)
            
            if isinstance(total_leads_contacted, (int, float, np.number)):
                 pivot_human = (pivot_human / total_leads_contacted) * 100
            else:
                 pivot_human = pivot_human.div(total_leads_contacted, axis=0) * 100
        else:
            pivot_human = pd.DataFrame()
            
        # Setup column config for dynamic columns
        column_config = {
            col: st.column_config.NumberColumn(format="%.2f%%") 
            for col in pivot_human.columns
        }
            
        st.dataframe(
            pivot_human,
            column_config=column_config,
            width='stretch'
        )

    # --- Section 5: Campaign Performance Table ---
    if key_prefix != "campaign":
        st.markdown("---")
        st.subheader("Campaign Performance")
    
    if not campaigns_df.empty and key_prefix != "campaign":
        # Select and Rename columns for display
        display_cols = {
            'workspace_name': 'Workspace',
            'Name': 'Campaign Name',
            'status': 'Status',
            'emails_sent': 'Emails Sent',
            'leads_contacted': 'Leads Contacted',
            'total_reply_rate': 'Reply Rate (%)',
            'bounce_rate': 'Bounce Rate (%)',
            'semantic_interested_reply_rate': 'Interested Rate (%)',
            'not_interested_reply_rate': 'Not Interested Rate (%)',
            'automated_reply_rate': 'Automated Rate (%)',
            'human_reply_rate': 'Human Reply Rate (%)',
            'replied': 'Unique Replies',
            'human_reply': 'Human Replies',
            'interested_sementic': 'Interested',
            'bounced': 'Bounces', 
            'created_at': 'Created Date',
            'not_interested': 'Not Interested',
            'automated_replies': 'Automated Replies'
        }
        
        # Prepare table df
        table_df = campaigns_df[list(display_cols.keys())]
        table_df = table_df.rename(columns=display_cols)
        
        # Format Reply Rate column to include count
        # Showing as: "33.0% (115)"
        table_df['Reply Rate (%)'] = table_df.apply(
            lambda x: f"{x['Reply Rate (%)']*100:.2f}% ({int(x['Unique Replies'])})", 
            axis=1
        )

        table_df['Bounce Rate (%)'] = table_df.apply(
            lambda x: f"{x['Bounce Rate (%)']*100:.2f}% ({int(x['Bounces'])})", 
            axis=1
        )

        table_df['Interested Rate (%)'] = table_df.apply(
            lambda x: f"{x['Interested Rate (%)']:.2f}% ({int(x['Interested'])})", 
            axis=1
        )

        table_df['Not Interested Rate (%)'] = table_df.apply(
            lambda x: f"{x['Not Interested Rate (%)']*100:.2f}% ({int(x['Not Interested'])})", 
            axis=1
        )

        table_df['Automated Rate (%)'] = table_df.apply(
            lambda x: f"{x['Automated Rate (%)']*100:.2f}% ({int(x['Automated Replies'])})", 
            axis=1
        )

        table_df['Human Reply Rate (%)'] = table_df.apply(
            lambda x: f"{x['Human Reply Rate (%)']*100:.2f}% ({int(x['Human Replies'])})", 
            axis=1
        )

        st.dataframe(
            table_df,
            column_config={
                "Reply Rate (%)": st.column_config.TextColumn("Reply Rate (%)"),
                "Bounce Rate (%)": st.column_config.TextColumn("Bounce Rate (%)"),
                "Created Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
            },
            hide_index=True,
            width='stretch'
        )
        
        # CSV Export
        csv = table_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"campaign_performance_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            key=f"{key_prefix}_download_csv"
        )

    # --- Section 6: Time Series Chart ---
    st.markdown("---")
    st.subheader("Activity Over Time")
    
    if not leads_df.empty and 'Date' in leads_df.columns:
        # Ensure date type
        leads_df['Date'] = pd.to_datetime(leads_df['Date']).dt.date
        
        # Aggregate by date
        daily_counts = leads_df.groupby('Date').agg({
             'lead_id': 'count', 
             'replies': lambda x: (x > 0).sum(),
             'bounce_type': lambda x: x.notna().sum()
        }).rename(columns={
            'lead_id': 'Total Activity', 
            'replies': 'Replies', 
            'bounce_type': 'Bounces'
        }).reset_index()
        
        # Melt for plotly
        melted = daily_counts.melt(id_vars=['Date'], var_name='Metric', value_name='Count')
        
        fig = px.line(
            melted,
            x='Date',
            y='Count',
            color='Metric',
            markers=True,
            color_discrete_sequence=PASTEL_PALETTE
        )
        
        update_chart_layout(fig, title='Daily Activity Trend')
        fig.update_xaxes(title=None, showgrid=False)
        fig.update_yaxes(title="Count", showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        fig.update_traces(line_shape='spline', line_width=3) # Smooth lines for style
        st.plotly_chart(fig, width='stretch')

def render_interested_leads_table(leads_df: pd.DataFrame, campaigns_df: pd.DataFrame):
    """
    Render the table of interested and objection leads.
    """
    # --- Section 7: Interested Leads Table ---
    st.markdown("---")
    st.subheader("Interested & Objection Leads")
    
    if not leads_df.empty and 'status' in leads_df.columns:
        # Filter for Interested or Objection
        # Note: 'Objection' might be 'Objections' or 'Objection' depending on exact enum
        target_statuses = ['Interested', 'Objection', 'Objections']
        interested_df = leads_df[leads_df['status'].isin(target_statuses)].copy()
        
        if not interested_df.empty:
            # Map campaign_id to Campaign Name
            if not campaigns_df.empty and 'campaign_id' in campaigns_df.columns and 'Name' in campaigns_df.columns:
                # Create separate dataframe for mapping to avoid index issues
                campaign_map = campaigns_df[['campaign_id', 'Name']].drop_duplicates('campaign_id').copy()
                
                # Normalize types to match leads_df (which is numeric)
                # Convert campaign_map['campaign_id'] to numeric, coercing errors
                campaign_map['campaign_id'] = pd.to_numeric(campaign_map['campaign_id'], errors='coerce')
                
                # Create mapping dictionary
                # Drop NaNs to avoid mapping issues
                campaign_map = campaign_map.dropna(subset=['campaign_id'])
                campaign_dict = dict(zip(campaign_map['campaign_id'], campaign_map['Name']))
                
                # Ensure leads_df ID is also treated as numeric (it should be, but just in case)
                interested_df['campaign_id'] = pd.to_numeric(interested_df['campaign_id'], errors='coerce')
                
                # Apply map
                interested_df['Campaign Name'] = interested_df['campaign_id'].map(campaign_dict).fillna('Unknown')
            else:
                 interested_df['Campaign Name'] = 'Unknown'

            # Determine which columns to show, prioritizing Lead Name first
            possible_cols = [
                'Full Name', # Combined Name
                'Campaign Name', 
                'email', 'Email', 
                'company', 'Company', 'company_name',
                'job_title', 'Job Title',
                'status', 
                'Date', 
            ]
            
            # Combine First and Last Name if present
            if 'first_name' in interested_df.columns and 'last_name' in interested_df.columns:
                interested_df['Full Name'] = interested_df['first_name'].fillna('') + ' ' + interested_df['last_name'].fillna('')
                interested_df['Full Name'] = interested_df['Full Name'].str.strip()
            elif 'Name' in interested_df.columns:
                 interested_df['Full Name'] = interested_df['Name']
            else:
                 interested_df['Full Name'] = 'Unknown'
            
            # Select existing columns
            cols_to_show = []
            for col in possible_cols:
                if col in interested_df.columns and col not in cols_to_show:
                    cols_to_show.append(col)
            
            # If no name/email columns found, fallback to all or a default set
            if len(cols_to_show) < 2:
                 cols_to_show = interested_df.columns.tolist()

            display_df = interested_df[cols_to_show]
            
            # Formatting for display
            def highlight_status(val):
                color = ''
                if val == 'Interested':
                    color = 'background-color: #d4edda; color: #155724' # Green
                elif val in ['Objection', 'Objections']:
                    color = 'background-color: #fff3cd; color: #856404' # Yellow
                return color

            st.dataframe(
                display_df.style.map(highlight_status, subset=['status']),
                hide_index=True,
                width='stretch'
            )
        else:
            st.info("No leads found with status 'Interested' or 'Objection'.")
