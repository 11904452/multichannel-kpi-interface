from typing import Dict, List, Optional
import pandas as pd

def calculate_percentage_change(current: float, previous: float) -> str:
    """
    Calculate percentage change and format as string with direction arrow.
    
    Returns:
        String like "↑ 12.5%" or "↓ 5.2%" or "0.0%"
    """
    if previous == 0:
        return "N/A" if current > 0 else "0.0%"
        
    change = ((current - previous) / previous) * 100
    arrow = "↑" if change >= 0 else "↓"
    return f"{arrow} {abs(change):.1f}%"

def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, returning 0.0 if denominator is 0."""
    return (numerator / denominator) if denominator != 0 else 0.0

def calculate_kpis(campaigns_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate high-level KPIs from campaigns dataframe.
    """
    if campaigns_df.empty:
        return {
            "total_sent": 0,
            "total_contacted": 0,
            "overall_reply_rate": 0.0,
            "bounce_rate": 0.0,
            "replies": 0,
            "bounces": 0,
            "human_reply_rate": 0.0,
            "human_replies": 0,
            "interested_rate": 0.0,
            "interested_replies": 0,
            "not_interested_rate": 0.0,
            "not_interested_replies": 0,
            "automated_rate": 0.0,
            "automated_replies": 0
        }
    # Sum counts where available
    #     
    # Sum counts where available
    total_sent = campaigns_df['emails_sent'].sum() if 'emails_sent' in campaigns_df.columns else 0
    total_contacted = campaigns_df['leads_contacted'].sum() if 'leads_contacted' in campaigns_df.columns else 0
    total_replies = campaigns_df['total_replies'].sum() if 'total_replies' in campaigns_df.columns else 0
    total_bounces = campaigns_df['bounced'].sum() if 'bounced' in campaigns_df.columns else 0
    
    human_replies = campaigns_df['human_reply'].sum() if 'human_reply' in campaigns_df.columns else 0
    
    # Try both spellings for semantic/sementic interested
    if 'interested_semantic' in campaigns_df.columns:
        interested_replies = campaigns_df['interested_semantic'].sum()
    elif 'interested_sementic' in campaigns_df.columns:
        interested_replies = campaigns_df['interested_sementic'].sum()
    else:
        interested_replies = 0
        
    not_interested = campaigns_df['not_interested'].sum() if 'not_interested' in campaigns_df.columns else 0
    automated_replies = campaigns_df['automated_replies'].sum() if 'automated_replies' in campaigns_df.columns else 0
    objection = campaigns_df['objection'].sum() if 'objection' in campaigns_df.columns else 0
    
    # Reply Rates
    bounce_rate = (total_bounces / total_contacted * 100) if total_contacted > 0 else 0
    total_reply_rate = (total_replies / total_contacted * 100) if total_contacted > 0 else 0
    human_reply_rate = (human_replies / total_contacted * 100) if total_contacted > 0 else 0
    automated_rate = (automated_replies / total_contacted * 100) if total_contacted > 0 else 0
    
    not_interested_replies = int(not_interested)
    automated_replies = int(automated_replies)

    interested_rate = (interested_replies / human_replies * 100) if human_replies > 0 else 0
    not_interested_rate = (not_interested / human_replies * 100) if human_replies > 0 else 0
    objection_rate = (objection / human_replies * 100) if human_replies > 0 else 0
    
    return {
        "total_sent": total_sent,
        "total_contacted": total_contacted,
        "overall_reply_rate": total_reply_rate,
        "bounce_rate": bounce_rate,
        "replies": total_replies,
        "bounces": total_bounces,
        "human_reply_rate": human_reply_rate,
        "human_replies": human_replies,
        "interested_rate": interested_rate,
        "interested_replies": interested_replies,
        "not_interested_rate": not_interested_rate,
        "not_interested_replies": not_interested_replies,
        "automated_rate": automated_rate,
        "automated_replies": automated_replies,
        "objection_rate": objection_rate,
        "objection": objection
    }

def calculate_campaign_kpis(campaign_row: pd.Series) -> Dict[str, float]:
    """
    Calculate KPIs for a single campaign.
    
    Args:
        campaign_row: A single row from campaigns dataframe
    
    Returns:
        Dictionary of KPI metrics for the campaign
    """
    if campaign_row.empty:
        return {
            "total_sent": 0,
            "total_contacted": 0,
            "overall_reply_rate": 0.0,
            "bounce_rate": 0.0,
            "replies": 0,
            "bounces": 0,
            "human_reply_rate": 0.0,
            "interested_rate": 0.0,
            "not_interested_rate": 0.0,
            "automated_rate": 0.0,
            "objection_rate": 0.0,
            "objection": 0
        }
    
    # Helper to safely get value (int or float)
    def get_val(key, default=0):
        return campaign_row.get(key, default)

    # Helper to retrieve rate (multiplies by 100 if it exists)
    def get_rate(key):
        return get_val(key, 0) * 100

    # Handle both spellings for interested
    interested_replies = get_val('interested_semantic') if 'interested_semantic' in campaign_row else get_val('interested_sementic', 0)
    interested_rate = get_rate('semantic_interested_reply_rate') if 'semantic_interested_reply_rate' in campaign_row else get_rate('sementic_interested_reply_rate')
    
    return {
        "total_sent": get_val('emails_sent'),
        "total_contacted": get_val('leads_contacted'),
        "overall_reply_rate": get_rate('total_reply_rate'),
        "bounce_rate": get_rate('bounce_rate'),
        "replies": get_val('total_replies'),
        "bounces": get_val('bounced'),
        "human_reply_rate": get_rate('human_reply_rate'),
        "human_replies": get_val('human_reply'),
        "interested_rate": interested_rate,
        "interested_replies": interested_replies,
        "not_interested_rate": get_rate('not_interested_reply_rate'),
        "not_interested_replies": int(get_val('not_interested')),
        "automated_rate": get_rate('automated_reply_rate'),
        "automated_replies": int(get_val('automated_replies')),
        "objection_rate": get_rate('objection_rate'),
        "objection": int(get_val('objection'))
    }

