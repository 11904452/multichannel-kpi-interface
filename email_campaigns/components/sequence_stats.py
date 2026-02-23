import streamlit as st
import pandas as pd

def render_sequence_stats(leads_df: pd.DataFrame, sequences_df: pd.DataFrame, campaign_stats=None):
    """
    Render individual email sequence stats
    """
    st.subheader("Individual Email Stats")
    
    if sequences_df.empty:
        st.info("No sequence steps found for this campaign.")
        return

    # Separate Parents and Variants
    # Parents are those where variant == False
    parents_df = sequences_df[sequences_df['variant'] == False].sort_values(by='order')
    variants_df = sequences_df[sequences_df['variant'] == True]

    # Helper function to render a single step card
    def render_step_card(step, is_variant=False, variant_counter=0, parent_order=0):
        step_id = step.get('sequence_num')
        order_num = int(step.get('order', 0))
        subject = step.get('subject', 'No Subject')
        
        # Determine Label
        if is_variant:
            # For variants, we might want to show "VARIANT X FOR STEP Y"
            step_label = f"VARIANT {variant_counter} FOR STEP {parent_order}"
            label_style = "color: gray; font-size: 0.9em; text-transform: uppercase;"
        else:
            step_label = f"STEP {order_num}"
            label_style = "color: gray; font-size: 0.9em; text-transform: uppercase;"

        # Stats Calculation
        # Use row-level data from sequences_df (step)
        sent_count = step.get('sent', 0)
        contacts_count = step.get('leads_contacted', 0)
        unique_replies = step.get('unique_replies', 0)
        interested = step.get('interested', 0)
        bounced = step.get('bounced', 0)

        # Render Row Card
        # Add visual differentiation for variants (indentation)
        margin_left = "50px" if is_variant else "0px"
        width_style = f"width: calc(100% - {margin_left});"
        
        # Gradient based on whether it's a variant or parent
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if not is_variant else "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        
        with st.container():
            st.markdown(f"""
            <style>
            .seq-card {{
                position: relative;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
                border: 1px solid #e2e8f0;
                margin-bottom: 12px;
                margin-left: {margin_left};
                {width_style}
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                overflow: hidden;
            }}
            
            .seq-card::before {{
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
            
            .seq-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
                border-color: #cbd5e1;
            }}
            
            .seq-card:hover::before {{
                width: 4px;
            }}
            
            .seq-label {{
                font-size: 0.65em;
                color: #64748b;
                margin-bottom: 6px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                position: relative;
                z-index: 1;
            }}
            
            .seq-subject {{
                font-weight: 500;
                font-size: 0.9em;
                color: #334155;
                margin-bottom: 12px;
                position: relative;
                z-index: 1;
            }}
            
            .metric-value {{
                font-size: 1.1em;
                font-weight: 700;
                color: #1e293b;
            }}
            
            .metric-label {{
                font-size: 0.65em;
                color: #64748b;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 2px;
            }}
            </style>
            <div class="seq-card">
            """, unsafe_allow_html=True)
            
            # Layout: Title (3) + 6 Stats (1 each)
            cols = st.columns([3, 1, 1, 1, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"<div class='seq-label'>{step_label}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='seq-subject'>{subject}</div>", unsafe_allow_html=True)

            # Calculate Stats from leads_df if available
            # Initialize with 0
            final_interested = 0
            final_not_interested = 0
            final_replies = 0
            final_bounced = 0
            
            if not leads_df.empty:
                step_cid = step.get('campaign_id')
                step_seq = step.get('sequence_num')
                
                # Ensure types match for filtering
                # leads_df['campaign_id'] and ['sequence_num'] are ints from data_processor
                try:
                    target_cid = int(step_cid) if pd.notna(step_cid) else -1
                    target_seq = int(step_seq) if pd.notna(step_seq) else -1
                    
                    matches = leads_df[
                        (leads_df['campaign_id'] == target_cid) & 
                        (leads_df['sequence_num'] == target_seq)
                    ]
                    
                    if not matches.empty:
                        # Count Interested (Interested, Objection)
                        # User requested "Interested", typically means purely Interested. 
                        # However, metrics often group Objection as a positive reply type or distinct.
                        # I'll include Objection to be safe as "Interested/Objection" is often desired,
                        # but user list had "Interested, Not interested". 
                        # I'll stick to 'Interested' + 'Objection' as a safe bet for "Positive/Neutral Response" block 
                        # OR if user meant specific columns: 'Interested'. 
                        # Given "take value of replies, Interested, Not interested, Bounced", 
                        # I will assume "Interested" means the status 'Interested'.
                        # But wait, previous code gathered Interest + Objection. 
                        # I will stick to the previous logic for "Is it a positive response?" but maybe label it properly?
                        # No, I will just count 'Interested'.
                        final_interested = matches[matches['status'] == 'Interested'].shape[0]
                        
                        # Count Not Interested
                        final_not_interested = matches[matches['status'] == 'Not Interested'].shape[0]

                        # Count Replies (Unique)
                        if 'unique_replies' in matches.columns:
                             final_replies = (matches['unique_replies'] >= 1).sum()
                        
                        # Count Bounced
                        # Check for bounce_type being present or status being 'Bounced'
                        # processor.py cleans bounce_type to string.
                        if 'bounce_type' in matches.columns:
                            # Count where bounce_type is not empty/null/nan
                            final_bounced = matches[matches['bounce_type'].str.len() > 0].shape[0]
                        elif 'status' in matches.columns:
                             final_bounced = matches[matches['status'] == 'Bounced'].shape[0]

                except Exception:
                    pass

            metrics = [
                ("Sent", sent_count, "📤"),
                ("Contacted", contacts_count, "👤"),
                ("Replies", final_replies, "💬"),
                ("Interested", final_interested, "⭐"),
                ("Not Interested", final_not_interested, "👎"),
                ("Bounced", final_bounced, "⚠️")
            ]
            
            for i, (label, value, icon) in enumerate(metrics):
                col_idx = i + 1
                if col_idx < len(cols):
                    with cols[col_idx]:
                        st.markdown(f"""
                        <div style='text-align: center;'>
                            <div class='metric-value'>{value}</div>
                            <div class='metric-label'>{label}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    # Iterate through parents and render them + their variants
    for _, parent_step in parents_df.iterrows():
        parent_seq_num = parent_step['sequence_num']
        parent_order = int(parent_step.get('order', 0))
        
        # Render Parent
        render_step_card(parent_step, is_variant=False)
        
        # Find Matches
        # variants where variant_from_step_id == parent_seq_num
        # Ensure strict type matching if needed, though they should be ints from data_processor
        matching_variants = variants_df[variants_df['variant_from_step_id'] == parent_seq_num]
        
        # Sort variants (optional, maybe by order or created time if available, or just index)
        # Assuming order might be same or specialized, just keep original sort or sort by sequence_num
        matching_variants = matching_variants.sort_values(by='sequence_num') 
        
        variant_count = 0
        for _, variant_step in matching_variants.iterrows():
            variant_count += 1
            render_step_card(variant_step, is_variant=True, variant_counter=variant_count, parent_order=parent_order)

    # Optional: Handle orphans (variants without a parent displayed above)
    # Ideally should not happen if data is consistent. 
    # If a variant has a parent that is NOT in this campaign, it won't be shown above.
    # The current logic loops through PARENTS first.
    # If we want to capture ALL steps, we might need a different approach if data is fragmented.
    # But assuming data integrity (all steps for campaign are fetched), this is fine.
