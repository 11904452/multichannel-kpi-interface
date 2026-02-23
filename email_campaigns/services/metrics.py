
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
    return f"{arrow} {abs(change):.2f}%"

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

def calculate_filtered_kpis(campaign_row: pd.Series, filtered_leads_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate KPIs based on filtered leads, but keep total sent/contacted from campaign.
    
    Args:
        campaign_row: The campaign data (for total counts)
        filtered_leads_df: The leads filtered by date
        
    Returns:
        Dictionary of KPIs
    """
    if campaign_row.empty:
        return calculate_campaign_kpis(campaign_row)

    # Base Totals (Unfiltered as requested)
    total_sent = campaign_row.get('emails_sent', 0)
    total_contacted = campaign_row.get('leads_contacted', 0)
    total_bounces_global = campaign_row.get('bounced', 0) # Bounces are usually tied to sent?
    # User only said "dont apply date range in people contacted".
    # I'll stick to `total_contacted` and `total_sent` being unfiltered.
    # Bounces: If I filter bounces by date, I need bounce date. Do we have it?
    # leads_df has 'Date' which is likely reply date or activity date.
    # If a bounce happened, does it have a Date? `DataProcessor` maps `Date` -> `date`.
    # Let's assume we calculate "Activities in this period".
    
    # Aggregations from filtered leads
    if filtered_leads_df.empty:
        # No activity in this period
        return {
            "total_sent": total_sent,
            "total_contacted": total_contacted,
            "overall_reply_rate": 0.0,
            "bounce_rate": 0.0,
            "replies": 0,
            "bounces": 0,
            # Bounces might technically be in the filtered_leads if status=Bounced?
            # But usually bounces are tracked separately or via status.
            # processor.py doesn't seem to agg bounces from leads directly in the `agg_stats` part?
            # It maps 'Bounced' from campaign data. 
            # BUT leads_df implies we have individual lead data.
            # Let's check processor.py again.. map: 'bounce_type'.
            # It doesn't seem to agg 'bounced' count from leads in `process_campaigns`.
            # Usage in metrics.py 'calculate_campaign_kpis' uses `get_val('bounced')`.
            # So bounces come from Campaign Table generally?
            # If so, we can't filter them by date unless we have a log.
            # I will use the Campaign Total for Bounces for now, or 0 if we assume "No activity".
            # Safest is to use Campaign Total for Bounces if we can't filter.
            # However, `replies` definitely comes from leads.
            
            "human_reply_rate": 0.0,
            "human_replies": 0,
            "interested_rate": 0.0,
            "interested_replies": 0,
            "not_interested_rate": 0.0,
            "not_interested_replies": 0,
            "automated_rate": 0.0,
            "automated_replies": 0,
            "objection_rate": 0.0,
            "objection": 0
        }

    # Calculations on filtered leads
    human_replies = filtered_leads_df['is_human_reply'].sum()
    
    # Status based counts
    # 'status' column.
    interested_replies = filtered_leads_df['status'].isin(['Interested']).sum()
    not_interested_replies = (filtered_leads_df['status'] == 'Not Interested').sum()
    automated_replies = (filtered_leads_df['status'] == 'Automated Reply').sum()
    objection_replies = filtered_leads_df['status'].isin(['Objection', 'Objections']).sum()
    
    # Total Replies (unique_replies >= 1)
    if 'unique_replies' in filtered_leads_df.columns:
         total_replies = (filtered_leads_df['unique_replies'] >= 1).sum()
    else:
         total_replies = 0

    # Rates based on Total Contacted (Unfiltered) as per "don't apply date range in people contacted"
    # This implies the denominator remains the same.
    
    total_reply_rate = (total_replies / total_contacted * 100) if total_contacted > 0 else 0
    human_reply_rate = (human_replies / total_contacted * 100) if total_contacted > 0 else 0
    automated_rate = (automated_replies / total_contacted * 100) if total_contacted > 0 else 0
    
    # Sub-rates (Denominator = Human Replies)
    interested_rate = (interested_replies / human_replies * 100) if human_replies > 0 else 0
    not_interested_rate = (not_interested_replies / human_replies * 100) if human_replies > 0 else 0
    objection_rate = (objection_replies / human_replies * 100) if human_replies > 0 else 0
    
    # Bounces in period?
    # If we treat bounces as an activity in leads table (e.g. status='Bounced'?)
    # `processor.py` didn't explicitly map 'Bounced' status -> count.
    # It just took 'bounced' column from campaign.
    # If we assume we can't date-filter bounces easily without more info, 
    # and the user focused on "Replies, status everything column that we are getting from leads table".
    # I will leave Bounce Rate as the Overall Campaign Bounce Rate for now, or just 0?
    # "status everything column... from leads table".
    # I'll just use the overall bounce rate from campaign_row to be safe, filtering only replies.
    
    bounce_rate = calculate_campaign_kpis(campaign_row)['bounce_rate']
    total_bounces = calculate_campaign_kpis(campaign_row)['bounces']

    return {
        "total_sent": total_sent,
        "total_contacted": total_contacted,
        "overall_reply_rate": total_reply_rate,
        "bounce_rate": bounce_rate,
        "replies": total_replies, # Filtered
        "bounces": total_bounces, # Unfiltered
        "human_reply_rate": human_reply_rate,
        "human_replies": human_replies, # Filtered
        "interested_rate": interested_rate,
        "interested_replies": interested_replies, # Filtered
        "not_interested_rate": not_interested_rate,
        "not_interested_replies": not_interested_replies, # Filtered
        "automated_rate": automated_rate,
        "automated_replies": automated_replies, # Filtered
        "objection_rate": objection_rate,
        "objection": objection_replies # Filtered
    }

def calculate_filtered_workspace_kpis(campaigns_df: pd.DataFrame, filtered_leads_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate KPIs for workspace overview based on filtered leads,
    while keeping total sent/contacted from campaigns (Unfiltered).
    
    Args:
        campaigns_df: The campaigns data (for total counts)
        filtered_leads_df: The leads filtered by date
        
    Returns:
        Dictionary of KPIs
    """
    if campaigns_df.empty:
        return calculate_kpis(campaigns_df) # Returns zeroed dict
        
    # 1. Base Totals (Unfiltered) from campaigns_df
    total_sent = campaigns_df['emails_sent'].sum() if 'emails_sent' in campaigns_df.columns else 0
    total_contacted = campaigns_df['leads_contacted'].sum() if 'leads_contacted' in campaigns_df.columns else 0
    total_bounces = campaigns_df['bounced'].sum() if 'bounced' in campaigns_df.columns else 0
    
    # 2. Aggregations from filtered leads
    if filtered_leads_df.empty:
        # No activity in this period
        return {
            "total_sent": total_sent,
            "total_contacted": total_contacted,
            "overall_reply_rate": 0.0,
            "bounce_rate": (total_bounces / total_contacted * 100) if total_contacted > 0 else 0,
            "replies": 0,
            "bounces": total_bounces,
            "human_reply_rate": 0.0,
            "human_replies": 0,
            "interested_rate": 0.0,
            "interested_replies": 0,
            "not_interested_rate": 0.0,
            "not_interested_replies": 0,
            "automated_rate": 0.0,
            "automated_replies": 0,
            "objection_rate": 0.0,
            "objection": 0
        }
        
    # Calculations on filtered leads
    human_replies = filtered_leads_df['is_human_reply'].sum()
    
    # Status based counts
    interested_replies = filtered_leads_df['status'].isin(['Interested']).sum()
    not_interested_replies = (filtered_leads_df['status'] == 'Not Interested').sum()
    automated_replies = (filtered_leads_df['status'] == 'Automated Reply').sum()
    objection_replies = filtered_leads_df['status'].isin(['Objection', 'Objections']).sum()
    
    # Total Replies
    if 'unique_replies' in filtered_leads_df.columns:
         total_replies = (filtered_leads_df['unique_replies'] >= 1).sum()
    else:
         total_replies = 0
         
    # Rates
    # Denominator: Total Contacted (Unfiltered)
    bounce_rate = (total_bounces / total_contacted * 100) if total_contacted > 0 else 0
    total_reply_rate = (total_replies / total_contacted * 100) if total_contacted > 0 else 0
    human_reply_rate = (human_replies / total_contacted * 100) if total_contacted > 0 else 0
    automated_rate = (automated_replies / total_contacted * 100) if total_contacted > 0 else 0
    
    # Sub-rates (Denominator: Human Replies)
    interested_rate = (interested_replies / human_replies * 100) if human_replies > 0 else 0
    not_interested_rate = (not_interested_replies / human_replies * 100) if human_replies > 0 else 0
    objection_rate = (objection_replies / human_replies * 100) if human_replies > 0 else 0
    
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
        "objection": objection_replies
    }
