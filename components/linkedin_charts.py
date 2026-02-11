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
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Lead Status Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
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

def render_top_recipients(leads_df):
    """Render top performing recipients analysis"""
    if leads_df.empty or 'recipient_name' not in leads_df.columns:
        st.info("No recipient data available")
        return
    
    st.subheader("🏆 Top Performing Recipients")
    
    # Aggregate by recipient
    recipient_stats = leads_df.groupby('recipient_name').agg({
        'lead_id': 'count',
        'replies': 'sum',
        'Status': lambda x: (x == 'Interested').sum()
    }).reset_index()
    
    recipient_stats.columns = ['Recipient', 'Total Leads', 'Total Replies', 'Interested Leads']
    recipient_stats['Interest Rate %'] = (recipient_stats['Interested Leads'] / recipient_stats['Total Leads'] * 100).round(2)
    recipient_stats = recipient_stats.sort_values('Interested Leads', ascending=False).head(10)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Horizontal bar chart
        fig = px.bar(
            recipient_stats,
            y='Recipient',
            x='Interested Leads',
            orientation='h',
            title="Top 10 Recipients by Interested Leads",
            color='Interest Rate %',
            color_continuous_scale='Viridis',
            text='Interested Leads'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top performer card
        if not recipient_stats.empty:
            top = recipient_stats.iloc[0]
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                <h3 style='margin:0; color: white;'>🥇 Top Performer</h3>
                <h2 style='margin:10px 0; color: white;'>{top['Recipient']}</h2>
                <p style='font-size: 24px; margin: 5px 0;'>{int(top['Interested Leads'])} Interested</p>
                <p style='font-size: 18px; margin: 5px 0;'>{top['Interest Rate %']:.1f}% Rate</p>
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
        fig.update_layout(height=400)
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
                height=400,
                yaxis_title="Rate (%)"
            )
            st.plotly_chart(fig, use_container_width=True)

def render_job_title_analysis(leads_df):
    """Render job title analysis"""
    if leads_df.empty or 'job_title' not in leads_df.columns:
        return
    
    st.subheader("💼 Job Title Insights")
    
    # Top job titles
    job_stats = leads_df.groupby('job_title').agg({
        'lead_id': 'count',
        'Status': lambda x: (x == 'Interested').sum()
    }).reset_index()
    job_stats.columns = ['Job Title', 'Total Leads', 'Interested']
    job_stats['Interest Rate %'] = (job_stats['Interested'] / job_stats['Total Leads'] * 100).round(2)
    job_stats = job_stats.sort_values('Interested', ascending=False).head(15)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            job_stats,
            x='Interest Rate %',
            y='Job Title',
            orientation='h',
            title="Top Job Titles by Interest Rate",
            color='Total Leads',
            color_continuous_scale='Blues',
            text='Interest Rate %'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Summary stats
        st.markdown("### Key Insights")
        total_titles = leads_df['job_title'].nunique()
        st.metric("Unique Job Titles", f"{total_titles:,}")
        
        if not job_stats.empty:
            best_title = job_stats.iloc[0]
            st.markdown(f"""
            **Most Responsive:**  
            {best_title['Job Title']}  
            *{best_title['Interest Rate %']:.1f}% interest rate*
            """)

def render_engagement_timeline(leads_df):
    """Render engagement timeline analysis"""
    if leads_df.empty or 'reply_date' not in leads_df.columns:
        return
    
    st.subheader("📅 Engagement Timeline")
    
    # Filter out null dates
    timeline_df = leads_df[leads_df['reply_date'].notna()].copy()
    
    if timeline_df.empty:
        st.info("No timeline data available")
        return
    
    timeline_df['date'] = pd.to_datetime(timeline_df['reply_date']).dt.date
    
    # Daily engagement
    daily_stats = timeline_df.groupby('date').agg({
        'lead_id': 'count',
        'Status': lambda x: (x == 'Interested').sum()
    }).reset_index()
    daily_stats.columns = ['Date', 'Total Replies', 'Interested']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_stats['Date'],
        y=daily_stats['Total Replies'],
        mode='lines+markers',
        name='Total Replies',
        line=dict(color='#667eea', width=3),
        fill='tozeroy'
    ))
    fig.add_trace(go.Scatter(
        x=daily_stats['Date'],
        y=daily_stats['Interested'],
        mode='lines+markers',
        name='Interested Leads',
        line=dict(color='#764ba2', width=3)
    ))
    
    fig.update_layout(
        title="Daily Engagement Trends",
        xaxis_title="Date",
        yaxis_title="Count",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def render_conversion_funnel(campaigns_df, leads_df):
    """Render enhanced conversion funnel"""
    st.subheader("🎯 Conversion Funnel")
    
    if campaigns_df.empty:
        st.info("No campaign data available")
        return
    
    # Calculate funnel metrics
    total_sent = campaigns_df['sent_connections'].sum()
    total_accepted = campaigns_df['accepted_connections'].sum()
    total_messages = campaigns_df['sent_messages'].sum()
    total_replies = campaigns_df['replies'].sum()
    
    interested = 0
    if not leads_df.empty and 'Status' in leads_df.columns:
        interested = len(leads_df[leads_df['Status'] == 'Interested'])
    
    funnel_data = pd.DataFrame({
        'Stage': ['Connections Sent', 'Connections Accepted', 'Messages Sent', 'Replies Received', 'Interested Leads'],
        'Count': [total_sent, total_accepted, total_messages, total_replies, interested]
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.funnel(
            funnel_data,
            x='Count',
            y='Stage',
            title="Complete Conversion Funnel"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Conversion rates
        st.markdown("### Conversion Rates")
        if total_sent > 0:
            st.metric("Connection → Acceptance", f"{(total_accepted/total_sent*100):.1f}%")
        if total_accepted > 0:
            st.metric("Accepted → Message", f"{(total_messages/total_accepted*100):.1f}%")
        if total_messages > 0:
            st.metric("Message → Reply", f"{(total_replies/total_messages*100):.1f}%")
        if total_replies > 0:
            st.metric("Reply → Interested", f"{(interested/total_replies*100):.1f}%")

def render_detailed_tables(campaigns_df, leads_df):
    """Render detailed data tables with enhanced styling"""
    st.subheader("📋 Detailed Data Tables")
    
    tab1, tab2 = st.tabs(["Campaign Details", "Lead Details"])
    
    with tab1:
        if not campaigns_df.empty:
            display_cols = [
                'campaign_name', 'workspace_name', 'Status', 'outreach_type',
                'sent_connections', 'accepted_connections', 'sent_messages', 
                'replies', 'sent_inmails', 'inmail_replies'
            ]
            cols = [c for c in display_cols if c in campaigns_df.columns]
            
            st.dataframe(
                campaigns_df[cols],
                use_container_width=True,
                column_config={
                    "campaign_name": st.column_config.TextColumn("Campaign", width="medium"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "sent_connections": st.column_config.NumberColumn("Sent", format="%d"),
                    "accepted_connections": st.column_config.NumberColumn("Accepted", format="%d"),
                    "replies": st.column_config.NumberColumn("Replies", format="%d")
                }
            )
    
    with tab2:
        if not leads_df.empty:
            display_cols = [
                'name', 'job_title', 'Status', 'recipient_name', 
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
                    "reply_date": st.column_config.DatetimeColumn("Reply Date", format="D MMM YYYY")
                }
            )
