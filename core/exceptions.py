"""
Custom exception classes for the application.

This module defines custom exceptions for better error handling
and more informative error messages throughout the application.
"""

from typing import Optional


class ApplicationError(Exception):
    """Base exception class for all application errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """
        Initialize the application error.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(ApplicationError):
    """Raised when database connection fails."""
    pass


class ValidationError(ApplicationError):
    """Raised when input validation fails."""
    pass


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    pass


class APIError(ApplicationError):
    """Raised when an API operation fails."""
    pass


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid or missing."""
    pass
