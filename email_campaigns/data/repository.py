"""
Email data repository for database operations.

This module handles all database operations for email campaigns,
leads, and sequences using the unified database client.
"""

from typing import List, Dict, Optional
import pandas as pd
import streamlit as st

from core.database import get_database_client
from core.logger import logger
import config


class EmailRepository:
    """Repository for email campaign data operations."""
    
    def __init__(self):
        """Initialize the email repository."""
        self.db = get_database_client()
        self.campaigns_table = config.CAMPAIGNS_TABLE_NAME
        self.leads_table = config.LEADS_TABLE_NAME
        self.sequences_table = config.EMAIL_SEQUENCE_TABLE_NAME
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_campaigns(_self) -> List[Dict]:
        """
        Fetch all email campaigns.
        
        Returns:
            List of campaign dictionaries
        """
        try:
            return _self.db.fetch_all(_self.campaigns_table)
        except Exception as e:
            logger.error(f"Error fetching campaigns: {e}")
            st.error(f"Failed to load campaigns: {str(e)}")
            return []
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_leads(_self) -> List[Dict]:
        """
        Fetch all email leads.
        
        Returns:
            List of lead dictionaries
        """
        try:
            return _self.db.fetch_all(_self.leads_table)
        except Exception as e:
            logger.error(f"Error fetching leads: {e}")
            st.error(f"Failed to load leads: {str(e)}")
            return []
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_sequences(_self) -> List[Dict]:
        """
        Fetch all email sequences.
        
        Returns:
            List of sequence dictionaries
        """
        try:
            return _self.db.fetch_all(_self.sequences_table)
        except Exception as e:
            logger.error(f"Error fetching sequences: {e}")
            st.error(f"Failed to load sequences: {str(e)}")
            return []
