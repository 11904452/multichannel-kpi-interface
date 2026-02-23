"""
LinkedIn business logic services.

This module contains business logic and helper functions for LinkedIn campaigns.
"""

import pandas as pd
from typing import Dict, Any


def get_replied_leads(leads_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter leads to get only those that have replied.
    
    A lead is considered to have replied if:
    - The 'replies' column exists
    - The 'replies' value is not null
    - The 'replies' value is greater than 0
    
    Args:
        leads_df: DataFrame of LinkedIn leads
        
    Returns:
        Filtered DataFrame containing only replied leads
    """
    if leads_df.empty or 'replies' not in leads_df.columns:
        return pd.DataFrame()
    
    # Filter for replied leads: replies is not null and > 0
    replied_mask = (leads_df['replies'].notna()) & (leads_df['replies'] > 0)
    return leads_df[replied_mask]


def count_replied_leads(leads_df: pd.DataFrame) -> int:
    """
    Count the number of leads that have replied.
    
    Args:
        leads_df: DataFrame of LinkedIn leads
        
    Returns:
        Count of replied leads
    """
    return len(get_replied_leads(leads_df))


def calculate_reply_metrics(leads_df: pd.DataFrame, campaigns_df: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Calculate reply-related metrics from leads data.
    
    Args:
        leads_df: DataFrame of LinkedIn leads
        campaigns_df: Optional DataFrame of campaigns for additional context
        
    Returns:
        Dictionary of reply metrics
    """
    replied_leads = get_replied_leads(leads_df)
    total_replied = len(replied_leads)
    
    metrics = {
        'total_replied': total_replied,
        'replied_leads_df': replied_leads
    }
    
    # Calculate status breakdown for replied leads
    if not replied_leads.empty and 'Status' in replied_leads.columns:
        metrics['interested'] = len(replied_leads[replied_leads['Status'] == 'Interested'])
        metrics['objection'] = len(replied_leads[replied_leads['Status'].isin(['Objection', 'Objections'])])
        metrics['revisit'] = len(replied_leads[replied_leads['Status'] == 'Revisit Later'])
        metrics['not_interested'] = len(replied_leads[replied_leads['Status'] == 'Not Interested'])
        metrics['automated'] = len(replied_leads[replied_leads['Status'] == 'Automated Reply'])
    
    return metrics
