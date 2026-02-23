import streamlit as st
import pandas as pd
from typing import Dict
from email_campaigns.services.metrics import calculate_percentage_change

def render_custom_metric(label, value_primary, value_secondary=None, bg_color="#ffffff", icon="📊"):
    """
    Render an enhanced custom metric card with modern design.
    """
    value_html = f"<div style='display: flex; align-items: baseline; gap: 8px;'><span style='font-size: 1.8em; font-weight: 700; color: #1e293b;'>{value_primary}</span>"
    if value_secondary:
        value_html += f"<span style='font-size: 1.1em; color: #64748b; font-weight: 500;'>({value_secondary})</span>"
    value_html += "</div>"

    import hashlib
    class_id = "kpi-" + hashlib.md5(label.encode()).hexdigest()[:8]

    # Create gradient overlay based on bg_color
    gradient_map = {
        "#E8F0FE": "linear-gradient(135deg, #6C63FF 0%, #a78bfa 100%)",
        "#F3E8FD": "linear-gradient(135deg, #a78bfa 0%, #38bdf8 100%)",
        "#E4F7FB": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "#FCE8E6": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "#E6F4EA": "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
        "#FEF7E0": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    }
    
    gradient = gradient_map.get(bg_color, "linear-gradient(135deg, #6C63FF 0%, #a78bfa 100%)")

    st.markdown(f"""
    <style>
    .{class_id} {{
        position: relative;
        background: white;
        padding: 24px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    
    .{class_id}::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: {gradient};
        opacity: 1;
        transition: width 0.3s ease;
    }}
    
    .{class_id}:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
        border-color: #cbd5e1;
    }}
    
    .{class_id}:hover::before {{
        width: 4px;
        background: {gradient};
    }}
    
    .{class_id} .icon {{
        font-size: 1.5em;
        margin-bottom: 8px;
        display: inline-block;
        opacity: 0.7;
        color: #64748b;
    }}
    
    .{class_id} .label {{
        font-size: 0.7em;
        color: #64748b;
        margin-bottom: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    .{class_id} .value {{
        position: relative;
        z-index: 1;
        line-height: normal;
    }}
    </style>
    <div class="{class_id}">
        <div>
            <div class="icon">{icon}</div>
            <div class="label" title="{label}">{label}</div>
        </div>
        <div class="value">
            {value_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_cards(current_metrics: Dict[str, float]):
    """
    Render rows of KPI cards with trends.
    """
    # Create 4 columns for the KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # with col1:
    #     render_custom_metric(
    #         label="Total Emails Sent",
    #         value_primary=f"{int(current_metrics['total_sent']):,}",
    #         bg_color="#E8F0FE",
    #         icon="📧"
    #     )
        
    with col1:
        render_custom_metric(
            label="People Contacted",
            value_primary=f"{int(current_metrics['total_contacted']):,}",
            bg_color="#F3E8FD",
            icon="👥"
        )
        
    with col2:
        render_custom_metric(
            label="Overall Reply Rate",
            value_primary=f"{current_metrics['overall_reply_rate']:.2f}%",
            value_secondary=int(current_metrics['replies']),
            bg_color="#E4F7FB",
            icon="💬"
        )
    
    with col3:
        render_custom_metric(
            label="Bounce Rate",
            value_primary=f"{current_metrics['bounce_rate']:.2f}%",
            value_secondary=int(current_metrics['bounces']),
            bg_color="#FCE8E6",
            icon="📭"
        )

    with col4:
        render_custom_metric(
            label="Automated Reply Rate",
            value_primary=f"{current_metrics['automated_rate']:.2f}%",
            value_secondary=int(current_metrics.get('automated_replies', 0)),
            bg_color="#FEF7E0",
            icon="🤖"
        )

    # Second row of KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        render_custom_metric(
            label="Human Reply Rate",
            value_primary=f"{current_metrics['human_reply_rate']:.2f}%",
            value_secondary=int(current_metrics.get('human_replies', 0)),
            bg_color="#E6F4EA",
            icon="👤"
        )
        
    with col6:
        render_custom_metric(
            label="Objection Reply Rate",
            value_primary=f"{current_metrics['objection_rate']:.2f}%",
            value_secondary=int(current_metrics.get('objection', 0)),
            bg_color="#FEF7E0",
            icon="⚠️"
        )
        
    with col7:
        render_custom_metric(
            label="Not Interested Reply Rate",
            value_primary=f"{current_metrics['not_interested_rate']:.2f}%",
            value_secondary=int(current_metrics.get('not_interested_replies', 0)),
            bg_color="#FCE8E6",
            icon="🚫"
        )

    with col8:
        render_custom_metric(
            label="Interested Reply Rate",
            value_primary=f"{current_metrics['interested_rate']:.2f}%",
            value_secondary=int(current_metrics.get('interested_replies', 0)),
            bg_color="#E6F4EA",
            icon="⭐"
        )
        
    # with col8:
    #     # Calculate contacted/sent ratio
    #     contacted_sent_ratio = (current_metrics['total_contacted'] / current_metrics['total_sent'] * 100) if current_metrics['total_sent'] > 0 else 0
    #     prev_contacted_sent_ratio = (previous_metrics['total_contacted'] / previous_metrics['total_sent'] * 100) if previous_metrics['total_sent'] > 0 else 0
    #     st.metric(
    #         label="Contact Rate",
    #         value=f"{contacted_sent_ratio:.2f}%",
    #         delta=calculate_percentage_change(contacted_sent_ratio, prev_contacted_sent_ratio)
    #     )
