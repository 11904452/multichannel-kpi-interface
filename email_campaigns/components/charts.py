import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import numpy as np
# Modern Professional color palettes
# Modern Professional color palettes - matching new reference
# MODERN_BLUE_SEQ   = ['#6366F1', '#818CF8', '#A5B4FC', '#C7D2FE'] # Indigo
# MODERN_GREEN_SEQ  = ['#10B981', '#34D399', '#6EE7B7', '#A7F3D0'] # Emerald
# MODERN_ROSE_SEQ   = ['#F43F5E', '#FB7185', '#FDA4AF', '#FECDD3'] # Rose
# MODERN_PURPLE_SEQ = ['#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE'] # Violet
# MODERN_AMBER_SEQ  = ['#F59E0B', '#FBBF24', '#FCD34D', '#FDE68A'] # Amber
# MODERN_ORANGE_SEQ = ['#F97316', '#FB923C', '#FDBA74', '#FFEDD5'] # Orange
# Professional & Formal color palettes
MODERN_BLUE_SEQ   = ['#1E40AF', '#3B82F6', '#93C5FD', '#DBEAFE']
MODERN_GREEN_SEQ  = ['#065F46', '#10B981', '#6EE7B7', '#D1FAE5']
MODERN_ROSE_SEQ   = ['#9F1239', '#F43F5E', '#FDA4AF', '#FFF1F2']
MODERN_PURPLE_SEQ = ['#5B21B6', '#8B5CF6', '#C4B5FD', '#EDE9FE']
MODERN_AMBER_SEQ  = ['#92400E', '#F59E0B', '#FCD34D', '#FEF3C7']
FORMAL_GRAY_SEQ   = ['#334155', '#475569', '#64748B', '#94A3B8', '#CBD5E1', '#E2E8F0', '#F1F5F9']
BG_FORMAL_LIGHT   = "#F8FAFC"

# Define calm pastel palette
PASTEL_PALETTE = [
    '#6366F1', # Indigo
    '#10B981', # Emerald
    '#F43F5E', # Rose
    '#8B5CF6', # Lavender
    '#F59E0B', # Amber
    '#EC4899', # Pink
    '#0EA5E9', # Sky
]

def update_chart_layout(fig, title="", show_legend=True, height=280, margin=dict(l=20, r=20, t=60, b=20), legend_orientation="h", bg_color="rgba(0,0,0,0)"):
    """Helper to apply consistent calm styling with compact sizing"""
    
    legend_config = dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=10)
    )
    
    if legend_orientation == "v":
        legend_config = dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        )

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=16, color="#1e293b", family="Inter, sans-serif"),
            x=0.05,
            xanchor='left',
            y=0.95,
            yanchor='top',
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(family="Inter, sans-serif", color="#64748b"),
        showlegend=show_legend,
        margin=margin,
        colorway=MODERN_BLUE_SEQ,
        height=height,
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Inter, sans-serif",
            bordercolor="rgba(255, 255, 255, 0.05)"
        ),
        legend=legend_config
    )
    # Modern grid and axes
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10, color="#94a3b8"))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.3)" if bg_color != "rgba(0,0,0,0)" else "#f1f5f9", zeroline=False, tickfont=dict(size=10, color="#94a3b8"))
    return fig

@st.dialog("⚠️ Confirm Deletion")
def _email_confirm_delete_dialog(campaign_id, campaign_name: str, index: int):
    """Dialog to confirm email campaign deletion (mirrors LinkedIn pattern)."""
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
        if st.button("✅ Yes, Delete", key=f"email_confirm_del_{campaign_id}_{index}",
                     type="primary", width="stretch"):
            from api.email_api import EmailCampaignAPI
            api = EmailCampaignAPI()
            with st.spinner("Deleting campaign..."):
                response = api.delete_campaign(str(campaign_id))

            if isinstance(response, dict) and response.get('success', False):
                st.session_state['email_delete_success'] = response.get(
                    'message', f"Campaign '{campaign_name}' deleted successfully!"
                )
                st.rerun()
            else:
                error_message = (
                    response.get('message', 'Failed to delete campaign')
                    if isinstance(response, dict) else str(response)
                )
                st.session_state['email_delete_error'] = error_message
                st.rerun()
    with col2:
        if st.button("❌ Cancel", key=f"email_cancel_del_{campaign_id}_{index}",
                     width="stretch"):
            st.rerun()


def render_charts(leads_df: pd.DataFrame, campaigns_df: pd.DataFrame, key_prefix: str = "default"):
    """
    Render dashboard charts in a compact, detailed grid layout matching the reference design.
    """
    if leads_df.empty:
        st.info("No data available to render charts.")
        return

    # Helper: Custom standard Plotly margin for small square cards
    SQUARE_MARGIN = dict(l=20, r=10, t=60, b=10)
    
    # Global Plotly Corner Rounding
    st.markdown("""
        <style>
        iframe[title="plotly.graph_objs._figure.Figure"], 
        .js-plotly-plot, 
        div[data-testid="stPlotlyChart"] {
            border-radius: 16px !important;
            overflow: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Section 1: Dashboard Metrics & Breakdown
    st.markdown("<h3 style='margin-bottom: 20px;'>Dashboard Metrics</h3>", unsafe_allow_html=True)
    
    r1_col1, r1_col2, r1_col3 = st.columns([1, 1.4, 1.2], gap="medium")

    # Column 1: Overall Reply Metrics
    with r1_col1:
        # Calculate rates
        if not campaigns_df.empty and 'leads_contacted' in campaigns_df.columns:
            total_leads = pd.to_numeric(campaigns_df['leads_contacted'], errors='coerce').fillna(0).sum()
        else:
            total_leads = len(leads_df)
            
        human_replies = leads_df['is_human_reply'].fillna(0).sum()
        total_replies = leads_df[leads_df['unique_replies'] > 0].fillna(0).shape[0]
        
        human_rate = (human_replies / total_leads * 100) if total_leads > 0 else 0
        overall_rate = (total_replies / total_leads * 100) if total_leads > 0 else 0

        st.markdown(f"""
            <div style='background: {BG_FORMAL_LIGHT}; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; height: 100%;'>
                <p style='font-size: 0.9rem; font-weight: 700; color: #0f172a; margin-bottom: 20px;'>Overall Highlights</p>
                <div style='margin-bottom: 20px;'>
                    <div style='display: flex; justify-content: space-between; font-size: 0.75rem; color: #475569; margin-bottom: 6px;'>
                        <span>Human Reply Rate</span>
                        <span style='font-weight: 600; color: #1e293b;'>{human_rate:.2f}%</span>
                    </div>
                    <div style='background: white; height: 8px; border-radius: 4px; border: 1px solid #f1f5f9;'>
                        <div style='background: #10B981; width: {min(human_rate, 100)}%; height: 100%; border-radius: 4px;'></div>
                    </div>
                </div>
                <div>
                    <div style='display: flex; justify-content: space-between; font-size: 0.75rem; color: #475569; margin-bottom: 6px;'>
                        <span>Overall Reply Rate</span>
                        <span style='font-weight: 600; color: #1e293b;'>{overall_rate:.2f}%</span>
                    </div>
                    <div style='background: white; height: 8px; border-radius: 4px; border: 1px solid #f1f5f9;'>
                        <div style='background: #3B82F6; width: {min(overall_rate, 100)}%; height: 100%; border-radius: 4px;'></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Column 2: Reply Type Breakdown
    with r1_col2:
        status_counts = leads_df['status'].value_counts()
        interested_stats = ['Interested', 'Not Interested', 'Objection', 'Automated Reply', 'Revisit Later', 'Bounced']
        data = pd.DataFrame({
            'Status': interested_stats,
            'Count': [status_counts.get(s, 0) for s in interested_stats]
        })
        
        colors = [MODERN_GREEN_SEQ[0], MODERN_ROSE_SEQ[0], MODERN_AMBER_SEQ[0], MODERN_PURPLE_SEQ[0], MODERN_BLUE_SEQ[1], MODERN_ROSE_SEQ[1]]
        
        REPLY_COLOR_MAP = {
            'Interested':      '#059669',  # strong green
            'Objection':       '#6EE7B7',  # medium soft green
            'Bounced':         '#A7F3D0',  # light green
            'Not Interested':  '#FCA5A5',  # soft red (stands out)
            'Automated Reply': '#34D399',  # emerald green
            'Revisit Later':   '#D1FAE5',  # very light green
        }

        fig = px.bar(data, x='Count', y='Status', orientation='h', color='Status',
                     color_discrete_map=REPLY_COLOR_MAP)
        update_chart_layout(fig, title='Reply Breakdown', show_legend=False, height=230, 
                            margin=dict(l=20, r=10, t=60, b=10), bg_color=BG_FORMAL_LIGHT)
        fig.update_traces(marker_cornerradius=8, width=0.6)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Column 3: Bounce Type Distribution
    # Column 3: Bounce Type Distribution
    with r1_col3:
        # Clean up bounce data for cleaner pie chart
        valid_bounces = leads_df[leads_df['bounce_type'].notna()].copy()
        # Filter commonly unhelpful categories
        exclude = ['', 'unknown', 'None', 'nan', 'null']
        valid_bounces = valid_bounces[~valid_bounces['bounce_type'].astype(str).str.lower().isin(exclude)]
        
        bounce_counts = valid_bounces['bounce_type'].value_counts()
        if not bounce_counts.empty:
            fig = px.pie(values=bounce_counts.values, names=bounce_counts.index, hole=0.7,
                         color_discrete_sequence=MODERN_PURPLE_SEQ)
            update_chart_layout(fig, title='Bounce Type', show_legend=True, height=230, 
                                margin=dict(l=20, r=80, t=60, b=10), legend_orientation="v", bg_color=BG_FORMAL_LIGHT)
            fig.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#ffffff', width=2)))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No detailed bounce analysis available")
    # Section 4: Campaign Performance
    # st.markdown("---")
    # st.markdown("<h3 style='margin-bottom: 20px;'>🔍 Campaign Performance</h3>", unsafe_allow_html=True)
    
    if key_prefix != "campaign":
        # st.markdown("<h3 style='margin-bottom: 20px;'>🔍 Campaign Performance</h3>", unsafe_allow_html=True)
        # High Bounce Campaigns Bar Chart (vertical/list style)
        if not campaigns_df.empty:
            if 'bounce_rate' not in campaigns_df.columns:
                campaigns_df['bounce_rate'] = (campaigns_df['bounced'] / campaigns_df['emails_sent'] * 100).fillna(0)
            
            top_b = campaigns_df.sort_values('bounce_rate', ascending=False).head(5)
            fig = px.bar(top_b, x='bounce_rate', y='Name', orientation='h', color='bounce_rate',
                         color_continuous_scale=['#DBEAFE', '#93C5FD', '#3B82F6', '#1E40AF', '#1e3a8a'],
                         labels={'bounce_rate': 'Bounce %'})
            fig.update_coloraxes(colorbar=dict(tickfont=dict(color='#64748b'), title=dict(font=dict(color='#64748b'))))
            update_chart_layout(fig, title='High Bounce Campaigns', show_legend=False, height=250, 
                                margin=dict(l=20, r=10, t=60, b=10), bg_color=BG_FORMAL_LIGHT)
            fig.update_traces(marker_cornerradius=10)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # --- ROW 3: ESP Performance Matrix ---
    if 'sender_inbox_esp' in leads_df.columns and 'lead_esp' in leads_df.columns:
        # st.markdown("---")
        st.markdown("<h3 style='margin-bottom: 20px;'>🌐 ESP Performance Matrix</h3>", unsafe_allow_html=True)
        
        df_pivot = leads_df.copy()
        # Logic requested by user
        df_pivot['is_reply_bool'] = pd.to_numeric(df_pivot['unique_replies'], errors='coerce').fillna(0) > 0
        df_pivot['is_human_reply_bool'] = pd.to_numeric(df_pivot['is_human_reply'], errors='coerce').fillna(0) > 0
        
        # Calculate leads contacted based on unique sender_inbox_esp count
        if df_pivot['sender_inbox_esp'].nunique() == 1:
            if not campaigns_df.empty and 'leads_contacted' in campaigns_df.columns:
                 total_leads_contacted = pd.to_numeric(campaigns_df['leads_contacted'], errors='coerce').fillna(0).sum()
            else:
                 total_leads_contacted = len(df_pivot)
        else:
            total_leads_contacted = df_pivot.groupby('sender_inbox_esp')['lead_id'].count()
            total_leads_contacted['Total'] = total_leads_contacted.sum()

        has_data = (total_leads_contacted.sum() > 0) if isinstance(total_leads_contacted, pd.Series) else (total_leads_contacted > 0)

        if has_data:
            esp_col_left, esp_col_right = st.columns([2, 1], gap="large")
            
            with esp_col_left:
                # 1. Total Reply Rate Matrix
                st.markdown("<p style='font-size: 0.9rem; font-weight: 700; color: #1e293b; margin-top: 10px;'>Total Reply Rate (%)</p>", unsafe_allow_html=True)
                p_total = pd.pivot_table(df_pivot, values='is_reply_bool', index='sender_inbox_esp', 
                                         columns='lead_esp', aggfunc='sum', margins=True, margins_name='Total').fillna(0)
                
                if isinstance(total_leads_contacted, (int, float, np.number)):
                    p_total = (p_total / total_leads_contacted) * 100
                else:
                    p_total = p_total.div(total_leads_contacted, axis=0) * 100
                
                st.dataframe(p_total.style.format("{:.2f}%").background_gradient(cmap='Blues'), use_container_width=True)

                # st.markdown("<br>", unsafe_allow_html=True)
                
                # 2. Human Reply Rate Matrix
                st.markdown("<p style='font-size: 0.9rem; font-weight: 700; color: #1e293b;'>Human Reply Rate (%)</p>", unsafe_allow_html=True)
                p_human = pd.pivot_table(df_pivot, values='is_human_reply_bool', index='sender_inbox_esp', 
                                         columns='lead_esp', aggfunc='sum', margins=True, margins_name='Total').fillna(0)
                
                if isinstance(total_leads_contacted, (int, float, np.number)):
                    p_human = (p_human / total_leads_contacted) * 100
                else:
                    p_human = p_human.div(total_leads_contacted, axis=0) * 100
                
                st.dataframe(p_human.style.format("{:.2f}%").background_gradient(cmap='Greens'), use_container_width=True)

            with esp_col_right:
                # 1. Lead ESP Distribution Pie
                if 'lead_esp' in df_pivot.columns:
                    l_counts = df_pivot['lead_esp'].value_counts()
                    if not l_counts.empty:
                        fig_l = px.pie(values=l_counts.values, names=l_counts.index, hole=0.7,
                                     color_discrete_sequence=MODERN_AMBER_SEQ)
                        update_chart_layout(fig_l, title='Lead ESP Dist.', show_legend=True, height=220, 
                                            margin=dict(l=20, r=80, t=60, b=10), legend_orientation="v", bg_color=BG_FORMAL_LIGHT)
                        fig_l.update_layout(paper_bgcolor=BG_FORMAL_LIGHT, plot_bgcolor=BG_FORMAL_LIGHT)
                        fig_l.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_l, use_container_width=True, config={'displayModeBar': False})
                
                # 2. Sender ESP Distribution Pie
                if 'sender_inbox_esp' in df_pivot.columns:
                    s_counts = df_pivot['sender_inbox_esp'].value_counts()
                    if not s_counts.empty:
                        fig_s = px.pie(values=s_counts.values, names=s_counts.index, hole=0.7,
                                     color_discrete_sequence=MODERN_PURPLE_SEQ)
                        update_chart_layout(fig_s, title='Sender ESP Dist.', show_legend=True, height=220, 
                                            margin=dict(l=20, r=80, t=60, b=10), legend_orientation="v", bg_color=BG_FORMAL_LIGHT)
                        fig_s.update_layout(paper_bgcolor=BG_FORMAL_LIGHT, plot_bgcolor=BG_FORMAL_LIGHT)
                        fig_s.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Insufficient data for ESP Matrix calculations.")

    # --- Performance Trends Section ---
    if 'Date' in leads_df.columns:
        # Performance Trends (title handled inside fig.update_layout)
        
        df_ts = leads_df.copy()
        df_ts['Date'] = pd.to_datetime(df_ts['Date'], errors='coerce').dt.date
        df_ts = df_ts[df_ts['Date'].notna()]
        
        all_dates = sorted(df_ts['Date'].unique())
        daily_df = pd.DataFrame({'Date': all_dates}).set_index('Date')
        
        # Map all requested metrics
        daily_df['Replies'] = df_ts[df_ts['unique_replies'] > 0].groupby('Date').size()
        daily_df['Interested'] = df_ts[df_ts['status'] == 'Interested'].groupby('Date').size()
        daily_df['Not Interested'] = df_ts[df_ts['status'] == 'Not Interested'].groupby('Date').size()
        daily_df['Objection'] = df_ts[df_ts['status'] == 'Objection'].groupby('Date').size()
        daily_df['Automated Reply'] = df_ts[df_ts['status'] == 'Automated Reply'].groupby('Date').size()
        daily_df['Revisit Later'] = df_ts[df_ts['status'] == 'Revisit Later'].groupby('Date').size()
        daily_df['Bounced'] = df_ts[df_ts['status'] == 'Bounced'].groupby('Date').size()
        
        daily_df = daily_df.fillna(0).reset_index()

        METRIC_CONF = {
            'Replies':         ('#6366F1', 'rgba(99,102,241,0.1)'),
            'Interested':      (MODERN_GREEN_SEQ[0], 'rgba(16,185,129,0.1)'),
            'Not Interested':  (MODERN_ROSE_SEQ[0], 'rgba(244,63,94,0.1)'),
            'Objection':       (MODERN_AMBER_SEQ[0], 'rgba(245,158,11,0.1)'),
            'Automated Reply': (MODERN_PURPLE_SEQ[0], 'rgba(139,92,246,0.1)'),
            'Revisit Later':   (MODERN_BLUE_SEQ[1], 'rgba(59,130,246,0.1)'),
            'Bounced':         (MODERN_ROSE_SEQ[1], 'rgba(244,63,94,0.1)')
        }
        
        col_pick, col_val = st.columns([2.5, 1])
        with col_pick:
            sel_met = st.radio("Metric Selection", list(METRIC_CONF.keys()), 
                               horizontal=True, label_visibility="collapsed", 
                               key=f"{key_prefix}_met_sel_trend_v2")
        
        line_col, fill_col = METRIC_CONF[sel_met]
        total_v = int(daily_df[sel_met].sum())
        
        with col_val:
            st.markdown(f"<div style='text-align: right;'><span style='color: #64748b; font-size: 0.8rem;'>Total {sel_met}:</span> <span style='font-size: 1.4rem; font-weight: 800; color: {line_col};'>+{total_v}</span></div>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_df['Date'], y=daily_df[sel_met],
            mode='lines', line=dict(color=line_col, width=3, shape='spline'),
            fill='tozeroy', fillcolor=fill_col,
            hovertemplate='%{x|%b %d}: <b>%{y}</b><extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="<b>Performance Trends</b>",
                font=dict(size=16, color="#1e293b", family="Inter, sans-serif"),
                x=0.05,
                xanchor='left',
                y=0.95,
                yanchor='top',
            ),
            height=260, margin=dict(l=40, r=20, t=60, b=40),
            hovermode='x unified', paper_bgcolor=BG_FORMAL_LIGHT, plot_bgcolor=BG_FORMAL_LIGHT
        )
        fig.update_xaxes(showgrid=False, tickformat="%b %d")
        fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # st.markdown("<br>", unsafe_allow_html=True)
        # st.subheader("Detailed Performance Table")

    if not campaigns_df.empty and key_prefix != "campaign":
        st.markdown("<h3 style='margin-bottom: 20px;'>📊 Detailed Performance Table</h3>", unsafe_allow_html=True)
        # CSV Export (above table)
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
            'total_replies': 'Unique Replies',
            'human_reply': 'Human Replies',
            'interested_sementic': 'Interested',
            'bounced': 'Bounces',
            'created_at': 'Created Date',
            'not_interested': 'Not Interested',
            'automated_replies': 'Automated Replies'
        }
        table_df = campaigns_df[list(display_cols.keys())].copy()
        table_df = table_df.rename(columns=display_cols)

        # Format rate columns
        table_df['Reply Rate (%)'] = table_df.apply(
            lambda x: f"{x['Reply Rate (%)']*100:.2f}% ({int(x['Unique Replies'])})", axis=1)
        table_df['Bounce Rate (%)'] = table_df.apply(
            lambda x: f"{x['Bounce Rate (%)']*100:.2f}% ({int(x['Bounces'])})", axis=1)
        table_df['Interested Rate (%)'] = table_df.apply(
            lambda x: f"{x['Interested Rate (%)']:.2f}% ({int(x['Interested'])})", axis=1)
        table_df['Not Interested Rate (%)'] = table_df.apply(
            lambda x: f"{x['Not Interested Rate (%)']*100:.2f}% ({int(x['Not Interested'])})", axis=1)
        table_df['Automated Rate (%)'] = table_df.apply(
            lambda x: f"{x['Automated Rate (%)']*100:.2f}% ({int(x['Automated Replies'])})", axis=1)
        table_df['Human Reply Rate (%)'] = table_df.apply(
            lambda x: f"{x['Human Reply Rate (%)']*100:.2f}% ({int(x['Human Replies'])})", axis=1)

        csv = table_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"campaign_performance_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            key=f"{key_prefix}_download_csv"
        )

        # --- Table header row ---
        h1, h2, h3, h4, h5, h6, h7, h8, h9, h10 = st.columns([2.5, 1.5, 1, 1, 1, 1, 1, 1, 1, 0.8])
        h1.markdown("**Campaign**")
        h2.markdown("**Workspace**")
        h3.markdown("**Status**")
        h4.markdown("**Sent**")
        h5.markdown("**Leads**")
        h6.markdown("**Reply Rate**")
        h7.markdown("**Bounce Rate**")
        h8.markdown("**Interested**")
        h9.markdown("**Human Reply**")
        h10.markdown("**Action**")
        st.divider()

        # --- Table rows ---
        for index, row in campaigns_df.iterrows():
            status = row.get('status', '')
            is_deleted = str(status).strip().lower() == 'deleted' if status else False

            c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns([2.5, 1.5, 1, 1, 1, 1, 1, 1, 1, 0.8])

            with c1:
                st.write(row.get('Name', ''))
            with c2:
                st.write(row.get('workspace_name', ''))
            with c3:
                if is_deleted:
                    st.markdown(
                        f"<span style='color:#ef5350;font-weight:600;'>{status}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.write(status)
            with c4:
                st.write(f"{int(row.get('emails_sent', 0))}")
            with c5:
                st.write(f"{int(row.get('leads_contacted', 0))}")
            with c6:
                rr = row.get('total_reply_rate', 0) or 0
                tr = int(row.get('total_replies', 0) or 0)
                st.write(f"{rr*100:.2f}% ({tr})")
            with c7:
                br = row.get('bounce_rate', 0) or 0
                bo = int(row.get('bounced', 0) or 0)
                st.write(f"{br*100:.2f}% ({bo})")
            with c8:
                ir = row.get('semantic_interested_reply_rate', 0) or 0
                ic = int(row.get('interested_sementic', 0) or 0)
                st.write(f"{ir:.2f}% ({ic})")
            with c9:
                hr = row.get('human_reply_rate', 0) or 0
                hc = int(row.get('human_reply', 0) or 0)
                st.write(f"{hr*100:.2f}% ({hc})")
            with c10:
                campaign_id = row.get('campaign_id')
                campaign_name = row.get('Name', 'Campaign')
                if st.button(
                    "🗑️",
                    key=f"email_del_{campaign_id}_{index}",
                    disabled=not is_deleted,
                    help="Delete Campaign (only available for DELETED campaigns)"
                ):
                    _email_confirm_delete_dialog(campaign_id, campaign_name, index)

            st.divider()


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
