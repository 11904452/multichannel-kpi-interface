from datetime import datetime, timedelta
from typing import Tuple, Optional
import pandas as pd

def get_date_range(filter_option: str, custom_start: Optional[datetime] = None, custom_end: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    Calculate start and end dates based on the selected filter option.
    Returns timezone-naive datetimes.
    
    Args:
        filter_option: Selected date filter option
        custom_start: Custom start date (if 'Custom Date Range' selected)
        custom_end: Custom end date (if 'Custom Date Range' selected)
        
    Returns:
        Tuple of (start_date, end_date) as timezone-naive datetimes
    """
    # Get current time as timezone-naive
    today = datetime.now()
    # Remove timezone info if present
    if hasattr(today, 'tzinfo') and today.tzinfo is not None:
        today = today.replace(tzinfo=None)
    
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

    elif filter_option == "All Time":
        # Return a very early start date to cover all records
        start_date = datetime(2000, 1, 1)
        return start_date, today

        
    elif filter_option == "Custom Date Range" and custom_start and custom_end:
        # Ensure timezone-naive
        if hasattr(custom_start, 'tzinfo') and custom_start.tzinfo is not None:
            custom_start = custom_start.replace(tzinfo=None)
        if hasattr(custom_end, 'tzinfo') and custom_end.tzinfo is not None:
            custom_end = custom_end.replace(tzinfo=None)
        
        # Ensure full day coverage for end date
        end_date = custom_end.replace(hour=23, minute=59, second=59)
        return custom_start, end_date
        
    # Default to Last 7 Days if no match
    return today_start - timedelta(days=7), today

def filter_dataframe_by_date(df: pd.DataFrame, date_column: str, start_date, end_date) -> pd.DataFrame:
    """
    Filter dataframe by date range.
    
    Args:
        df: DataFrame to filter
        date_column: Name of the date column
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or date_column not in df.columns:
        return df
    
    # Ensure the date column is datetime
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    except Exception:
        return df
    
    # Convert start_date and end_date to timezone-naive if they are timezone-aware
    # This prevents comparison errors between tz-naive and tz-aware datetimes
    if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)
    if hasattr(end_date, 'tzinfo') and end_date.tzinfo is not None:
        end_date = end_date.replace(tzinfo=None)
    
    # Ensure the DataFrame column is also timezone-naive
    if hasattr(df[date_column].dtype, 'tz') and df[date_column].dtype.tz is not None:
        df[date_column] = df[date_column].dt.tz_localize(None)
    
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df.loc[mask]
