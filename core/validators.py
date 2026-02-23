"""
Input validation utilities for the application.

This module provides validation functions for common input types
like campaign IDs, dates, emails, etc.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.exceptions import ValidationError


def validate_campaign_id(campaign_id: Any) -> str:
    """
    Validate and normalize a campaign ID.
    
    Args:
        campaign_id: Campaign ID to validate
        
    Returns:
        Validated campaign ID as string
        
    Raises:
        ValidationError: If campaign ID is invalid
    """
    if campaign_id is None:
        raise ValidationError("Campaign ID cannot be None")
    
    campaign_id_str = str(campaign_id).strip()
    
    if not campaign_id_str:
        raise ValidationError("Campaign ID cannot be empty")
    
    return campaign_id_str


def validate_email(email: str) -> str:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated email address
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email cannot be empty")
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    
    return email.lower().strip()


def validate_date_range(start_date: datetime, end_date: datetime) -> tuple:
    """
    Validate a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple of (start_date, end_date)
        
    Raises:
        ValidationError: If date range is invalid
    """
    if start_date > end_date:
        raise ValidationError(
            f"Start date ({start_date}) cannot be after end date ({end_date})"
        )
    
    return start_date, end_date


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )


def validate_positive_number(value: Any, field_name: str) -> float:
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Validated number as float
        
    Raises:
        ValidationError: If value is not a positive number
    """
    try:
        num_value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number, got: {type(value).__name__}")
    
    if num_value < 0:
        raise ValidationError(f"{field_name} must be positive, got: {num_value}")
    
    return num_value


def validate_status(status: str, valid_statuses: List[str]) -> str:
    """
    Validate that a status is in the list of valid statuses.
    
    Args:
        status: Status to validate
        valid_statuses: List of valid status values
        
    Returns:
        Validated status
        
    Raises:
        ValidationError: If status is invalid
    """
    if status not in valid_statuses:
        raise ValidationError(
            f"Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}",
            details={"valid_statuses": valid_statuses}
        )
    
    return status
