"""
Reusable UI components for the dashboard.

This module provides common UI components used across both
email and LinkedIn dashboards.
"""

import streamlit as st
from pathlib import Path


def load_css(css_file: str = "assets/styles.css") -> None:
    """
    Load CSS from external file.

    Args:
        css_file: Path to CSS file relative to project root
    """
    # Resolve relative to this file's parent (the project root),
    # so it works regardless of the working directory (e.g. on Modal).
    project_root = Path(__file__).parent.parent
    css_path = project_root / css_file

    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {css_file}")


def render_platform_selector(show_api_alert: bool = False) -> str:
    """
    Render the platform selector in the sidebar.
    
    Args:
        show_api_alert: Whether to show an alert icon on API Config
        
    Returns:
        Selected platform ("📧 Email" or "🔗 LinkedIn")
    """
    st.markdown("""
    <style>
    /* Segmented Control Styling */
    div[data-testid="stRadio"][data-baseweb="radio"] > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    
    div[data-testid="stRadio"] > div > label {
        background-color: transparent;
        border-radius: 8px;
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
        text-align: center;
        border: none;
        margin: 0;
    }
    
    div[data-testid="stRadio"] > div > label:hover {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
    }
    
    div[data-testid="stRadio"] > div > label[data-baseweb="radio"] > div:first-child {
        display: none;
    }
    
    /* Active state */
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    div[data-testid="stRadio"] label:has(input:checked) p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0; font-size: 1.8em;'>🚀 Dashboard</h2>
        <p style='color: rgba(255,255,255,0.7); font-size: 0.9em; margin: 5px 0 0 0;'>Select Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    def format_func(option):
        if option == "🔑 API Config" and show_api_alert:
            return "🔑 API Config 🔴"
        return option
    
    platform = st.radio(
        "platform_selector_label",
        ["📧 Email", "🔗 LinkedIn", "🔑 API Config"],
        index=0,
        key="platform_selector",
        horizontal=True,
        label_visibility="collapsed",
        format_func=format_func
    )
    
    st.divider()
    return platform


def render_refresh_button() -> None:
    """Render a refresh button that clears cache and reruns the app."""
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()


def show_error(message: str, details: str = None) -> None:
    """
    Display an error message to the user.
    
    Args:
        message: Main error message
        details: Optional detailed error information
    """
    st.error(f"❌ {message}")
    if details:
        with st.expander("Error Details"):
            st.code(details)


def show_success(message: str) -> None:
    """
    Display a success message to the user.
    
    Args:
        message: Success message
    """
    st.success(f"✅ {message}")


def show_info(message: str) -> None:
    """
    Display an info message to the user.
    
    Args:
        message: Info message
    """
    st.info(f"ℹ️ {message}")
