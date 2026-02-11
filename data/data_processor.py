import pandas as pd
from typing import List, Dict
from datetime import datetime
import streamlit as st

class DataProcessor:
    """Handles data transformation and cleaning"""
    
    @staticmethod
    def process_leads(leads_data: List[Dict]) -> pd.DataFrame:
        """Convert lead dictionaries to DataFrame and clean types"""
        if not leads_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(leads_data)
        
        # Ensure required columns exist
        required_cols = ['Date', 'status', 'bounce_type', 'is_human_reply', 'replies', 'sender_inbox_esp', 'lead_esp']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
                
        # Boolean/Numeric conversions
        df['is_human_reply'] = pd.to_numeric(df['is_human_reply'], errors='coerce').fillna(0)
        df['replies'] = pd.to_numeric(df['replies'], errors='coerce').fillna(0)
        
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
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        return df

    @staticmethod
    def process_campaigns(campaigns_data: List[Dict]) -> pd.DataFrame:
        """Convert campaign dictionaries to DataFrame and clean types"""
        if not campaigns_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(campaigns_data)
        
        # Ensure numeric columns are actually numeric
        numeric_cols = [
            'emails_sent', 'replied', 'bounced', 'leads_contacted', 'human_reply', 
            'interested_sementic', 'campaign_id', 'not_interested', 'automated_replies',
            'unique_replied'
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

        # Recalculate Rates to ensure they are floats and correct
        # total_reply_rate
        if 'unique_replied' in df.columns and 'leads_contacted' in df.columns:
             df['total_reply_rate'] = (df['unique_replied'] / df['leads_contacted']).fillna(0)
             
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
        if 'automated_replies' in df.columns and 'human_reply' in df.columns:
             df['automated_reply_rate'] = df.apply(
                 lambda x: (x['automated_replies'] / x['human_reply']) if x['human_reply'] > 0 else 0, 
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
