"""
Unified database client for Supabase operations.

This module provides a centralized Supabase client with connection pooling,
retry logic, and comprehensive error handling.
"""

import os
from typing import List, Dict, Optional, Any
from functools import wraps
import time

import streamlit as st
from supabase import create_client, Client

from core.exceptions import DatabaseConnectionError, ResourceNotFoundError
from core.logger import logger
import config


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry database operations on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}"
                    )
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator


class DatabaseClient:
    """
    Unified database client for Supabase operations.
    
    This class handles all database connections and provides methods
    for CRUD operations with proper error handling and logging.
    """
    
    _instance: Optional['DatabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the database client."""
        if self._client is not None:
            return  # Already initialized
        
        self.url = config.SUPABASE_URL
        self.key = config.SUPABASE_KEY
        
        if not self.url or not self.key:
            error_msg = "Supabase credentials not found. Please check your .env file."
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
        
        try:
            self._client = create_client(self.url, self.key)
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            error_msg = f"Failed to initialize Supabase connection: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            raise DatabaseConnectionError("Database client not initialized")
        return self._client
    
    @retry_on_failure(max_retries=3)
    def fetch_all(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Fetch all records from a table with optional filters.
        
        Args:
            table_name: Name of the table
            filters: Optional dictionary of filters (column: value)
            
        Returns:
            List of records as dictionaries
            
        Raises:
            DatabaseConnectionError: If database operation fails
        """
        try:
            all_records = []
            offset = 0
            limit = 1000
            
            while True:
                query = self.client.table(table_name).select("*").range(offset, offset + limit - 1)
                
                # Apply filters if provided
                if filters:
                    for column, value in filters.items():
                        query = query.eq(column, value)
                
                response = query.execute()
                data = response.data
                
                if not data:
                    break
                    
                all_records.extend(data)
                
                if len(data) < limit:
                    break
                    
                offset += limit
                
            logger.debug(f"Fetched {len(all_records)} records from {table_name}")
            return all_records
            
        except Exception as e:
            error_msg = f"Error fetching from {table_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    @retry_on_failure(max_retries=3)
    def fetch_by_id(self, table_name: str, id_column: str, id_value: Any) -> Dict:
        """
        Fetch a single record by ID.
        
        Args:
            table_name: Name of the table
            id_column: Name of the ID column
            id_value: Value of the ID
            
        Returns:
            Record as dictionary
            
        Raises:
            ResourceNotFoundError: If record not found
            DatabaseConnectionError: If database operation fails
        """
        try:
            response = self.client.table(table_name).select("*").eq(id_column, id_value).execute()
            
            if not response.data:
                raise ResourceNotFoundError(
                    f"Record not found in {table_name} with {id_column}={id_value}"
                )
            
            logger.debug(f"Fetched record from {table_name} with {id_column}={id_value}")
            return response.data[0]
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Error fetching from {table_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    @retry_on_failure(max_retries=3)
    def insert(self, table_name: str, data: Dict[str, Any]) -> Dict:
        """
        Insert a new record.
        
        Args:
            table_name: Name of the table
            data: Dictionary of column: value pairs
            
        Returns:
            Inserted record as dictionary
            
        Raises:
            DatabaseConnectionError: If database operation fails
        """
        try:
            response = self.client.table(table_name).insert(data).execute()
            logger.info(f"Inserted record into {table_name}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            error_msg = f"Error inserting into {table_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    @retry_on_failure(max_retries=3)
    def update(self, table_name: str, id_column: str, id_value: Any, data: Dict[str, Any]) -> Dict:
        """
        Update an existing record.
        
        Args:
            table_name: Name of the table
            id_column: Name of the ID column
            id_value: Value of the ID
            data: Dictionary of column: value pairs to update
            
        Returns:
            Updated record as dictionary
            
        Raises:
            DatabaseConnectionError: If database operation fails
        """
        try:
            response = self.client.table(table_name).update(data).eq(id_column, id_value).execute()
            logger.info(f"Updated record in {table_name} with {id_column}={id_value}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            error_msg = f"Error updating {table_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    @retry_on_failure(max_retries=3)
    def delete(self, table_name: str, id_column: str, id_value: Any) -> bool:
        """
        Delete a record.
        
        Args:
            table_name: Name of the table
            id_column: Name of the ID column
            id_value: Value of the ID
            
        Returns:
            True if successful
            
        Raises:
            DatabaseConnectionError: If database operation fails
        """
        try:
            self.client.table(table_name).delete().eq(id_column, id_value).execute()
            logger.info(f"Deleted record from {table_name} with {id_column}={id_value}")
            return True
            
        except Exception as e:
            error_msg = f"Error deleting from {table_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    @retry_on_failure(max_retries=3)
    def delete_many(self, table_name: str, filters: Dict[str, Any]) -> bool:
        """
        Delete multiple records matching filters.
        
        Args:
            table_name: Name of the table
            filters: Dictionary of filters (column: value)
            
        Returns:
            True if successful
            
        Raises:
            DatabaseConnectionError: If database operation fails
        """
        try:
            query = self.client.table(table_name).delete()
            
            for column, value in filters.items():
                query = query.eq(column, value)
            
            query.execute()
            logger.info(f"Deleted records from {table_name} with filters: {filters}")
            return True
            
        except Exception as e:
            error_msg = f"Error deleting from {table_name}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg)
    
    def delete_linkedin_campaign(self, campaign_id: str) -> bool:
        """
        Delete a LinkedIn campaign. 
        Since cascade delete is configured in the database, 
        deleting the campaign will automatically delete associated leads.
        
        Args:
            campaign_id: ID of the campaign to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from config import LINKEDIN_CAMPAIGN_TABLE_NAME
            
            if not LINKEDIN_CAMPAIGN_TABLE_NAME:
                logger.error("LinkedIn campaign table name not configured")
                return False
            
            # Only delete from campaign table - cascade will handle leads
            result = self.delete(LINKEDIN_CAMPAIGN_TABLE_NAME, 'campaign_id', campaign_id)
            
            if result:
                logger.info(f"Successfully deleted LinkedIn campaign {campaign_id}")
                return True
            else:
                logger.warning(f"No campaign found with ID {campaign_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting LinkedIn campaign {campaign_id}: {str(e)}")
            return False


# Singleton instance
_db_client: Optional[DatabaseClient] = None


def get_database_client() -> DatabaseClient:
    """
    Get the singleton database client instance.
    
    Returns:
        DatabaseClient instance
    """
    global _db_client
    
    if _db_client is None:
        _db_client = DatabaseClient()
    
    return _db_client
