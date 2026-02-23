"""
Email Campaign Dashboard - Main Application Entry Point

A production-ready dashboard for managing and analyzing email and LinkedIn campaigns.
Clean, modular architecture with separated concerns.
"""

import streamlit as st

# Import shared utilities
from shared.ui_components import load_css, render_platform_selector, render_refresh_button
from components.api_key_manager import check_for_missing_keys

# Page configuration
st.set_page_config(
    page_title="📧 Email KPI Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS from external file
load_css()


def main():
    """Main application entry point."""
    
    # Check for missing API keys to show alert
    has_missing_keys = check_for_missing_keys()
    
    # Sidebar Platform Selection
    with st.sidebar:
        platform = render_platform_selector(show_api_alert=has_missing_keys)
    
    # Route to appropriate dashboard based on platform selection
    # Route to appropriate dashboard based on platform selection
    if platform == "🔗 LinkedIn":
        from linkedin.components.dashboard import render_linkedin_dashboard
        render_linkedin_dashboard()
    elif platform == "🔑 API Config":
        from components.api_key_manager import render_api_key_manager
        render_api_key_manager()
    else:
        from email_campaigns.components.dashboard import run_email_dashboard
        run_email_dashboard()
    
    # Refresh button in sidebar (Bottom)
    with st.sidebar:
        st.divider()
        render_refresh_button()
        
        # Math Guide
        from shared.guide import render_math_guide
        render_math_guide()


if __name__ == "__main__":
    main()
