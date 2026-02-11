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
    Renders the cute robot helper in the sidebar.
    """
    # Container for the robot helper
    with st.container():
        st.markdown("""<div style="height: 20px;"></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display robot image
            # Assuming 'assets/robot.png' exists. 
            # If not, it will fail gracefully or show broken image, 
            # but we should check or use a placeholder if missing.
            if os.path.exists("assets/robot.png"):
                st.image("assets/robot.png", width=80)
            else:
                st.write("🤖")
                
        with col2:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                padding: 12px 16px;
                border-radius: 16px;
                border-bottom-left-radius: 4px;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25), 
                            0 2px 8px rgba(102, 126, 234, 0.2),
                            inset 0 1px 0 rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(255, 255, 255, 0.4);
                font-size: 0.88em;
                color: #1e293b;
                margin-left: -10px;
                margin-bottom: 8px;
                font-weight: 500;
                position: relative;
            ">
            <div style="
                position: absolute;
                left: -8px;
                bottom: 0;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 0 8px 8px 0;
                border-color: transparent #ffffff transparent transparent;
            "></div>
            <b style="color: #667eea; font-size: 1.05em;">Hi there! 👋</b><br>
            <span style="color: #475569;">Need help with the math?</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Open Guide 📘", key="open_math_guide", help="Open the Math Helper Notebook"):
                guide_dialog()
