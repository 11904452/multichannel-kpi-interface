import pandas as pd
from typing import List, Dict
from datetime import datetime
import streamlit as st

class DataProcessor:
    """Handles data transformation and cleaning"""
    
    @staticmethod
    def _normalize_columns(df: pd.DataFrame, mappings: Dict[str, str] = None):
        """Helper to normalize column names (e.g. name -> Name)"""
        if df.empty:
            return df
            
        # Standardize to lowercase for checking, but keep original if not mapping
        # Actually, simpler: just rename found columns if they exist
        if mappings:
            # Check for different casings
            existing_cols = set(df.columns)
            rename_map = {}
            for target_col, variants in mappings.items():
                if target_col in existing_cols:
                    continue # Already exists
                
                for variant in variants:
                    if variant in existing_cols:
                        rename_map[variant] = target_col
                        break
            
            if rename_map:
                df = df.rename(columns=rename_map)
                
        return df
    
    @staticmethod
    def process_leads(leads_data: List[Dict]) -> pd.DataFrame:
        """Convert lead dictionaries to DataFrame and clean types"""
        if not leads_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(leads_data)
        
        # Normalize columns: Supabase might be lowercase
        # Map: lowercase -> Expected Capitalized
        df = DataProcessor._normalize_columns(df, {
            'Date': ['date'],
            'status': ['Status'],
            'is_human_reply': ['Is Human Reply'],
            'bounce_type': ['Bounce Type'],
            'sender_inbox_esp': ['Sender Inbox ESP'],
            'lead_esp': ['Lead ESP'],
            'campaign_id': ['Campaign ID', 'campaign_id'], # Ensure snake_case
            'sequence_num': ['Sequence Num', 'sequence_num'],
            'unique_replies': ['Unique Replies', 'unique_replies']
        })
        
        # Ensure required columns exist
        required_cols = ['Date', 'status', 'bounce_type', 'is_human_reply', 'replies', 'sender_inbox_esp', 'lead_esp', 'unique_replies']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
                
        # Boolean/Numeric conversions
        df['is_human_reply'] = pd.to_numeric(df['is_human_reply'], errors='coerce').fillna(0)
        df['replies'] = pd.to_numeric(df['replies'], errors='coerce').fillna(0)
        df['unique_replies'] = pd.to_numeric(df['unique_replies'], errors='coerce').fillna(0)
        
        # Ensure ID columns are numeric for joining
        id_cols = ['sequence_num', 'campaign_id']
        for col in id_cols:
            if col in df.columns:
                # Handle lists if present (Airtable Linked Records)
                df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x)
                # Now convert to numeric and strictly cast to integer
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # specific string cleaning
        string_cols = ['status', 'bounce_type', 'sender_inbox_esp', 'lead_esp']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Date conversion
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        return df

    @staticmethod
    def process_campaigns(campaigns_data: List[Dict], leads_df: pd.DataFrame = None) -> pd.DataFrame:
        """Convert campaign dictionaries to DataFrame and clean types, including aggregations from leads"""
        if not campaigns_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(campaigns_data)
        
        # Normalize columns
        df = DataProcessor._normalize_columns(df, {
            'Name': ['name'],
            'workspace_name': ['Workspace Name'],
            'campaign_id': ['Campaign ID'],
            'created_at': ['Created At'],
            'emails_sent': ['Emails Sent'],
            'leads_contacted': ['Leads Contacted'],
            'replied': ['Replied'],
            'bounced': ['Bounced'],
            'unique_replied': ['Unique Replied']
        })
        
        # --- Aggregation from Leads (Backfill missing Supabase columns) ---
        if leads_df is not None and not leads_df.empty and 'campaign_id' in leads_df.columns:
            # Group by campaign_id
            # 1. Human Replies: count where is_human_reply is true
            # 2. Interested: status in ['Interested', 'Objection'] (Mapped to 'interested_sementic')
            # 3. Not Interested: status == 'Not Interested'
            # 4. Automated: status == 'Automated Reply'
            
            # Helper to sum boolean/condition
            def count_cond(x, col, val):
                return (x[col] == val).sum()
                
            def count_in(x, col, vals):
                return x[col].isin(vals).sum()

            # Create aggregation map
            # We need to act on the leads_df and merge back to df (campaigns)
            
            # Ensure proper types for merging
            leads_df['campaign_id'] = pd.to_numeric(leads_df['campaign_id'], errors='coerce').fillna(0).astype(int)
            
            agg_stats = leads_df.groupby('campaign_id').agg(
                human_reply=('is_human_reply', 'sum'), # is_human_reply is 1/0 or True/False
                interested_sementic=('status', lambda x: x.isin(['Interested']).sum()),
                not_interested=('status', lambda x: (x == 'Not Interested').sum()),
                automated_replies=('status', lambda x: (x == 'Automated Reply').sum()),
                total_replies=('unique_replies',lambda x: (x >= 1).sum()),
                objection=('status', lambda x: x.isin(['Objection', 'Objections']).sum()),
                
            ).reset_index()

            # Merge aggregated stats into campaigns df
            # First ensure campaign_id in campaigns is int
            if 'campaign_id' in df.columns:
                 # Handle lists if needed (though Supabase usually gives direct values)
                 df['campaign_id'] = df['campaign_id'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x)
                 df['campaign_id'] = pd.to_numeric(df['campaign_id'], errors='coerce').fillna(0).astype(int)
            
            df = df.merge(agg_stats, on='campaign_id', how='left', suffixes=('', '_calc'))
            
            # Fill missing calculated values with 0 (for campaigns with no leads)
            calc_cols = ['human_reply', 'interested_sementic', 'not_interested', 'automated_replies', 'total_replies','objection']
            for col in calc_cols:
                # If column existed (from Supabase) but we want to override or fill
                # The prompt says Supabase DOES NOT have these, so they will be NaN after merge or from original
                
                # If merge created suffixes (e.g. human_reply exists in orig data), use calculated one or prefer one?
                # User said: "campaign table have same columns except..." implying these columns are MISSING in Supabase.
                # So they likely won't exist in original df, or be null.
                # The merge puts them in.
                if col not in df.columns:
                    df[col] = 0
                else:
                    df[col] = df[col].fillna(0)
                    
                # If there was a collision and we successfully merged, we might have col and col_calc?
                # But if original didn't have it, we are good.
                # If original had it (e.g. empty column), we should allow overwrite.
                
                # To be safe, if `col_calc` exists, copy to `col` and drop `col_calc`
                if f'{col}_calc' in df.columns:
                    df[col] = df[f'{col}_calc'].fillna(0)
                    df.drop(columns=[f'{col}_calc'], inplace=True)

        # Ensure numeric columns are actually numeric
        numeric_cols = [
            'emails_sent', 'replied', 'bounced', 'leads_contacted', 'human_reply', 
            'interested_sementic', 'campaign_id', 'not_interested', 'automated_replies',
            'unique_replied', 'total_replies', 'objection'
        ]
        for col in numeric_cols:
            if col in df.columns:
                # Handle lists if present (Airtable Linked Records/Lookups)
                df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                if col == 'campaign_id':
                     df[col] = df[col].astype(int)
            else:
                df[col] = 0
                
        # Date conversion
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            
        # Clean Name column (Single Select handling)
        if 'Name' in df.columns:
            df['Name'] = df['Name'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else str(x) if x else 'Unknown')
        else:
             # If mapping failed and name is missing completely
             df['Name'] = 'Unknown Campaign'

        # Recalculate Rates to ensure they are floats and correct
        # total_reply_rate
        if 'total_replies' in df.columns and 'leads_contacted' in df.columns:
             df['total_reply_rate'] = (df['total_replies'] / df['leads_contacted']).fillna(0)
             
        # bounce_rate
        if 'bounced' in df.columns and 'leads_contacted' in df.columns:
             df['bounce_rate'] = (df['bounced'] / df['leads_contacted']).fillna(0)
             
        # human_reply_rate (vs leads contacted)
        if 'human_reply' in df.columns and 'leads_contacted' in df.columns:
             df['human_reply_rate'] = (df['human_reply'] / df['leads_contacted']).fillna(0)

        # semantic_interested_reply_rate (vs human replies)
        if 'interested_sementic' in df.columns and 'human_reply' in df.columns:
             # Calculate rate, handle division by zero
             df['semantic_interested_reply_rate'] = df.apply(
                 lambda x: (x['interested_sementic'] / x['human_reply']) if x['human_reply'] > 0 else 0, 
                 axis=1
             )

        # not_interested_reply_rate (vs human replies)
        if 'not_interested' in df.columns and 'human_reply' in df.columns:
             df['not_interested_reply_rate'] = df.apply(
                 lambda x: (x['not_interested'] / x['human_reply']) if x['human_reply'] > 0 else 0, 
                 axis=1
             )

        # automated_reply_rate (vs human replies? or vs total? usually vs human for categorization or total for noise)
        # charts.py uses: automated_replies / human_reply
        if 'automated_replies' in df.columns and 'leads_contacted' in df.columns:
             df['automated_reply_rate'] = df.apply(
                 lambda x: (x['automated_replies'] / x['leads_contacted']) if x['leads_contacted'] > 0 else 0, 
                 axis=1
             )

        if 'objection' in df.columns and 'human_reply' in df.columns:
             df['objection_rate'] = df.apply(
                 lambda x: (x['objection'] / x['human_reply']) if x['human_reply'] > 0 else 0, 
                 axis=1
             )
             
        return df

    @staticmethod
    def process_email_sequences(sequences_data: List[Dict]) -> pd.DataFrame:
        """Convert email sequence dictionaries to DataFrame and clean types"""
        if not sequences_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(sequences_data)
        
        # Ensure numeric columns
        numeric_cols = ['sequence_num', 'campaign_id', 'order', 'wait_in_days', 'variant_from_step_id', 'sequence_id']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
                
        # Boolean columns
        # variant and thread_reply are Single Select(True/False) so they might come as strings "True"/"False" or simple booleans
        # User said "Single SELECT(True/False)"
        bool_cols = ['variant', 'thread_reply']
        for col in bool_cols:
            if col in df.columns:
                # Handle string "True"/"False" from single select
                df[col] = df[col].astype(str).str.lower().apply(lambda x: x == 'true')
            else:
                df[col] = False

        # Text columns
        if 'subject' not in df.columns:
            df['subject'] = ""
        else:
            df['subject'] = df['subject'].astype(str)

        return df
