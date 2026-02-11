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
            "bounces": 0
        }
    # Sum counts where available
    #     
    total_sent = campaigns_df['emails_sent'].sum()
    total_contacted = campaigns_df['leads_contacted'].sum()
    total_replies = campaigns_df['replied'].sum()
    total_bounces = campaigns_df['bounced'].sum()
    human_replies = campaigns_df['human_reply'].sum() if 'human_reply' in campaigns_df.columns else 0
    interested_replies = campaigns_df['interested_sementic'].sum() if 'interested_sementic' in campaigns_df.columns else 0
    not_interested = campaigns_df['not_interested'].sum()
    automated_replies = campaigns_df['automated_replies'].sum()
    
    # Reply Rates
    bounce_rate = (total_bounces / total_contacted) * 100
    total_reply_rate = (total_replies / total_contacted) * 100
    human_reply_rate = (human_replies / total_contacted) * 100
    automated_rate = (automated_replies / total_contacted) * 100
    not_interested_replies = int(not_interested)
    automated_replies = int(automated_replies)

    interested_rate = (interested_replies / human_replies) * 100
    not_interested_rate = (not_interested / human_replies) * 100
    
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
        "automated_replies": automated_replies
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
            "automated_rate": 0.0
        }
    
    return {
        "total_sent": campaign_row.get('emails_sent', 0),
        "total_contacted": campaign_row.get('leads_contacted', 0),
        "overall_reply_rate": campaign_row.get('total_reply_rate', 0) * 100,
        "bounce_rate": campaign_row.get('bounce_rate', 0) * 100,
        "replies": campaign_row.get('replied', 0),
        "bounces": campaign_row.get('bounced', 0),
        "human_reply_rate": campaign_row.get('human_reply_rate', 0) * 100,
        "human_replies": campaign_row.get('human_reply', 0),
        "interested_rate": campaign_row.get('semantic_interested_reply_rate', 0) * 100,
        "interested_replies": campaign_row.get('interested_sementic', 0),
        # Estimate missing counts
        "not_interested_rate": campaign_row.get('not_interested_reply_rate', 0) * 100,
        "not_interested_replies": int(campaign_row.get('not_interested', 0)),
        "automated_rate": campaign_row.get('automated_reply_rate', 0) * 100,
        "automated_replies": int(campaign_row.get('automated_replies', 0))
    }

