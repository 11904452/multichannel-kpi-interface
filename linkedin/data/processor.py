"""
LinkedIn data processor for type conversions and data cleaning.

This module handles data processing specific to LinkedIn campaigns and leads.
"""

import pandas as pd
from typing import List, Dict


class LinkedInDataProcessor:
    """Processor for LinkedIn campaign and lead data."""
    
    @staticmethod
    def process_campaigns(campaigns_data: List[Dict]) -> pd.DataFrame:
        """
        Process LinkedIn campaigns data.
        
        Args:
            campaigns_data: List of campaign dictionaries from database
            
        Returns:
            Processed DataFrame
        """
        if not campaigns_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(campaigns_data)
        
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
    def process_leads(leads_data: List[Dict]) -> pd.DataFrame:
        """
        Process LinkedIn leads data.
        
        Args:
            leads_data: List of lead dictionaries from database
            
        Returns:
            Processed DataFrame
        """
        if not leads_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(leads_data)
        
        # Type conversions
        if 'reply_date' in df.columns:
            df['reply_date'] = pd.to_datetime(df['reply_date'], errors='coerce')
        
        if 'createdTime' in df.columns:
            df['createdTime'] = pd.to_datetime(df['createdTime'], errors='coerce')
        
        # Numeric conversions
        if 'replies' in df.columns:
            df['replies'] = pd.to_numeric(df['replies'], errors='coerce').fillna(0)
        
        return df
