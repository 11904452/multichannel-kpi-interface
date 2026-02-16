import pandas as pd
from data.supabase_client import SupabaseClient
import streamlit as st

class LinkedinDataLoader:
    @staticmethod
    def get_linkedin_campaigns():
        """Returns linkedin campaigns dataframe from Supabase"""
        client = SupabaseClient()
        data = client.get_linkedin_campaigns()
        
        if not data:
             return pd.DataFrame()

        df = pd.DataFrame(data)
        
        # Numeric conversions
        numeric_cols = [
            'sent_connections', 'accepted_connections', 'sent_messages', 
            'replies', 'inmail_replies', 'sent_inmails', 
            'audience_size', 'target_count', 'complete'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Date conversions
        if 'date' in df.columns:
             df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df

    @staticmethod
    def get_linkedin_leads():
        """Returns linkedin leads dataframe from Supabase"""
        client = SupabaseClient()
        data = client.get_linkedin_leads()
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Type conversions
        if 'reply_date' in df.columns:
            df['reply_date'] = pd.to_datetime(df['reply_date'], errors='coerce')
            
        if 'createdTime' in df.columns:
            df['createdTime'] = pd.to_datetime(df['createdTime'], errors='coerce')

        # Numeric conversions
        if 'replies' in df.columns:
            df['replies'] = pd.to_numeric(df['replies'], errors='coerce').fillna(0)
            
        return df

    @staticmethod
    def delete_campaign(campaign_id: str) -> bool:
        """Deletes a campaign and its data"""
        client = SupabaseClient()
        return client.delete_linkedin_campaign(campaign_id)
