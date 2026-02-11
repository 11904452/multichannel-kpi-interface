import streamlit as st
import pandas as pd
from components.kpi_cards import render_custom_metric

def calculate_linkedin_metrics(df):
    """Calculate aggregated metrics from linkedin campaigns dataframe"""
    if df.empty:
        return {}
    
    total_sent_connections = df['sent_connections'].sum()
    total_accepted = df['accepted_connections'].sum()
    total_sent_messages = df['sent_messages'].sum()
    total_replies = df['replies'].sum()
    total_sent_inmails = df['sent_inmails'].sum()
    total_inmail_replies = df['inmail_replies'].sum()
    
    acceptance_rate = (total_accepted / total_sent_connections * 100) if total_sent_connections > 0 else 0
    reply_rate = (total_replies / total_sent_messages * 100) if total_sent_messages > 0 else 0
    inmail_reply_rate = (total_inmail_replies / total_sent_inmails * 100) if total_sent_inmails > 0 else 0
    
    return {
        "sent_connections": total_sent_connections,
        "accepted_connections": total_accepted,
        "acceptance_rate": acceptance_rate,
        "sent_messages": total_sent_messages,
        "replies": total_replies,
        "reply_rate": reply_rate,
        "sent_inmails": total_sent_inmails,
        "inmail_replies": total_inmail_replies,
        "inmail_reply_rate": inmail_reply_rate
    }

def render_linkedin_kpi_cards(metrics):
    """Render enhanced KPI cards for Linkedin with comprehensive metrics"""
    
    # First Row - Primary Engagement Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_custom_metric(
            label="Acceptance Rate",
            value_primary=f"{metrics.get('acceptance_rate', 0):.2f}%",
            value_secondary=f"{int(metrics.get('accepted_connections', 0)):,}",
            bg_color="#E8F0FE",
            icon="🤝"
        )
        
    with col2:
        render_custom_metric(
            label="Reply Rate",
            value_primary=f"{metrics.get('reply_rate', 0):.2f}%",
            value_secondary=f"{int(metrics.get('replies', 0)):,}",
            bg_color="#E4F7FB",
            icon="💬"
        )
        
    with col3:
        render_custom_metric(
            label="InMail Reply Rate",
            value_primary=f"{metrics.get('inmail_reply_rate', 0):.2f}%",
            value_secondary=f"{int(metrics.get('inmail_replies', 0)):,}",
            bg_color="#F3E8FD",
            icon="📨"
        )

    with col4:
        # Calculate overall conversion rate (connections to replies)
        total_sent = metrics.get('sent_connections', 0)
        total_replies = metrics.get('replies', 0)
        conversion_rate = (total_replies / total_sent * 100) if total_sent > 0 else 0
        
        render_custom_metric(
            label="Overall Conversion",
            value_primary=f"{conversion_rate:.2f}%",
            value_secondary="Connect → Reply",
            bg_color="#E6F4EA",
            icon="🎯"
        )
    
    # Second Row - Volume Metrics
    cols2 = st.columns(4)
    
    with cols2[0]:
         render_custom_metric(
             label="Sent Connections", 
             value_primary=f"{int(metrics.get('sent_connections', 0)):,}",
             bg_color="#FEF7E0",
             icon="🔗"
        )
         
    with cols2[1]:
         render_custom_metric(
             label="Sent Messages", 
             value_primary=f"{int(metrics.get('sent_messages', 0)):,}",
             bg_color="#E6F4EA",
             icon="📤"
        )
    
    with cols2[2]:
         render_custom_metric(
             label="Sent InMails", 
             value_primary=f"{int(metrics.get('sent_inmails', 0)):,}",
             bg_color="#FCE8E6",
             icon="📮"
        )
    
    with cols2[3]:
        # Calculate message-to-reply conversion
        msg_to_reply = (metrics.get('replies', 0) / metrics.get('sent_messages', 1) * 100)
        render_custom_metric(
            label="Message Effectiveness",
            value_primary=f"{msg_to_reply:.1f}%",
            value_secondary="Msg → Reply",
            bg_color="#E8F0FE",
            icon="⚡"
        )

