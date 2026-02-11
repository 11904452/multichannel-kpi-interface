from datetime import datetime, timedelta
from typing import Tuple, Optional
import pandas as pd

def get_date_range(filter_option: str, custom_start: Optional[datetime] = None, custom_end: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    Calculate start and end dates based on the selected filter option.
    
    Args:
        filter_option: Selected date filter option
        custom_start: Custom start date (if 'Custom Date Range' selected)
        custom_end: Custom end date (if 'Custom Date Range' selected)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if filter_option == "Today":
        return today_start, today
        
    elif filter_option == "This Week":
        # Monday to Sunday
        start_date = today_start - timedelta(days=today.weekday())
        return start_date, today
        
    elif filter_option == "Last Week":
        start_date = today_start - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start_date, end_date
        
    elif filter_option == "Last 7 Days":
        start_date = today_start - timedelta(days=7)
        return start_date, today
        
    elif filter_option == "Last 30 Days":
        start_date = today_start - timedelta(days=30)
        return start_date, today
        
    elif filter_option == "This Month":
        start_date = today_start.replace(day=1)
        return start_date, today
        
    elif filter_option == "Last Month":
        last_month_end = today_start.replace(day=1) - timedelta(seconds=1)
        start_date = last_month_end.replace(day=1)
        return start_date, last_month_end
        
    elif filter_option == "Custom Date Range" and custom_start and custom_end:
        # Ensure full day coverage for end date
        end_date = custom_end.replace(hour=23, minute=59, second=59)
        return custom_start, end_date
        
    # Default to Last 7 Days if no match
    return today_start - timedelta(days=7), today

def filter_dataframe_by_date(df: pd.DataFrame, date_column: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Filter DataFrame rows where date_column is within [start_date, end_date].
    """
    if df.empty or date_column not in df.columns:
        return df
        
    # Ensure column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        try:
            df[date_column] = pd.to_datetime(df[date_column])
        except Exception:
            return df
            
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df.loc[mask]
