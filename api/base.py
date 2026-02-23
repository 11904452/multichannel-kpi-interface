"""
Base API handler with common functionality.

This module provides base classes and decorators for API operations
including error handling, logging, and response formatting.
"""

from typing import Any, Dict, Callable
from functools import wraps

from core.logger import logger
from core.exceptions import ApplicationError, ValidationError, DatabaseConnectionError


class APIResponse:
    """Standard API response format."""
    
    @staticmethod
    def success(data: Any, message: str = "Success") -> Dict[str, Any]:
        """
        Create a success response.
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Formatted response dictionary
        """
        return {
            "success": True,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create an error response.
        
        Args:
            message: Error message
            details: Optional error details
            
        Returns:
            Formatted error dictionary
        """
        return {
            "success": False,
            "message": message,
            "details": details or {}
        }


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle API errors consistently.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {e.message}")
            return APIResponse.error(e.message, e.details)
        except DatabaseConnectionError as e:
            logger.error(f"Database error in {func.__name__}: {e.message}")
            return APIResponse.error("Database connection failed. Please try again.", e.details)
        except ApplicationError as e:
            logger.error(f"Application error in {func.__name__}: {e.message}")
            return APIResponse.error(e.message, e.details)
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}")
            return APIResponse.error("An unexpected error occurred. Please contact support.")
    
    return wrapper


def log_api_call(func: Callable) -> Callable:
    """
    Decorator to log API calls.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"API call: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"API call completed: {func.__name__}")
        return result
    
    return wrapper
