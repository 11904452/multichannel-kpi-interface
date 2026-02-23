import streamlit as st
import os

# Try to use st.dialog (Streamlit 1.34+), fallback to experimental if needed
if hasattr(st, "dialog"):
    dialog_decorator = st.dialog
elif hasattr(st, "experimental_dialog"):
    dialog_decorator = st.experimental_dialog
else:
    # Fallback for very old versions (though we updated requirements)
    def dialog_decorator(title):
        def wrapper(func):
            return func
        return wrapper

@dialog_decorator("📚 Math Helper Notebook")
def guide_dialog():
    st.markdown("""
    <style>
        /* Custom styling for the notebook dialog */
        div[data-testid="stDialog"] {
            background-color: #fcfbf9; /* Paper-like background */
            border-radius: 15px;
            border: 2px solid #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🧮 KPI Formulas & Guide
    
    <div style="font-size: 0.9em; color: #555; font-style: italic;">
    "Here is the secret sauce behind the numbers!" 🤖
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # 1. Bounce Rate
    st.markdown("#### 1. Bounce Rate 📉")
    st.caption("Percentage of emails that didn't reach the recipient.")
    st.latex(r'''
        Rate = \frac{\text{Total Bounces}}{\text{Total Contacted}} \times 100
    ''')
    st.info("💡 **Tip:** High bounce rates (>5%) can hurt your domain reputation.", icon="🧹")

    st.divider()

    # 2. Overall Reply Rate
    st.markdown("#### 2. Reply Rate (Overall) 📬")
    st.caption("All replies, including auto-responses.")
    st.latex(r'''
        Rate = \frac{\text{Total Replies}}{\text{Total Contacted}} \times 100
    ''')

    st.divider()

    # 3. Human Reply Rate
    st.markdown("#### 3. Human Reply Rate 👤")
    st.caption("Real people replying (excluding bots).")
    st.latex(r'''
        Rate = \frac{\text{Human Replies}}{\text{Total Contacted}} \times 100
    ''')
    st.success("🌟 **Goal:** This is your most important metric!", icon="🎯")

    st.divider()

    # 4. Interested Rate
    st.markdown("#### 4. Interested Rate 🤩")
    st.caption("Percentage of **human** replies that are positive.")
    st.latex(r'''
        Rate = \frac{\text{Interested Replies}}{\text{Human Replies}} \times 100
    ''')

    st.divider()
    
    st.caption("📝 *Data is processed automatically.*")

def render_math_guide():
    """
    Renders the math guide button in the sidebar.
    """
    # Container for the guide button
    with st.container():
        st.markdown("""<div style="height: 10px;"></div>""", unsafe_allow_html=True)
        
        if st.button("📘 Formulae Book", key="open_math_guide", help="Open the Math Helper Notebook", width="stretch"):
            guide_dialog()
