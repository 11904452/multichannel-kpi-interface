"""
LinkedIn data repository for database operations.

This module handles all database operations for LinkedIn campaigns and leads
using the unified database client and API layer.
"""

import pandas as pd
import streamlit as st
from typing import List, Dict

from core.database import get_database_client
from core.logger import logger
from linkedin.data.processor import LinkedInDataProcessor
import config


class LinkedInRepository:
    """Repository for LinkedIn campaign data operations."""
    
    def __init__(self):
        """Initialize the LinkedIn repository."""
        self.db = get_database_client()
        self.campaigns_table = config.LINKEDIN_CAMPAIGN_TABLE_NAME
        self.leads_table = config.LINKEDIN_LEADS_TABLE_NAME
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_campaigns(_self) -> pd.DataFrame:
        """
        Fetch and process LinkedIn campaigns.
        
        Returns:
            Processed DataFrame of campaigns
        """
        try:
            data = _self.db.fetch_all(_self.campaigns_table)
            return LinkedInDataProcessor.process_campaigns(data)
        except Exception as e:
            logger.error(f"Error fetching LinkedIn campaigns: {e}")
            st.error(f"Failed to load campaigns: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_leads(_self) -> pd.DataFrame:
        """
        Fetch and process LinkedIn leads.
        
        Returns:
            Processed DataFrame of leads
        """
        try:
            data = _self.db.fetch_all(_self.leads_table)
            return LinkedInDataProcessor.process_leads(data)
        except Exception as e:
            logger.error(f"Error fetching LinkedIn leads: {e}")
            st.error(f"Failed to load leads: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_accounts(_self) -> pd.DataFrame:
        """
        Fetch LinkedIn accounts.
        
        Returns:
            DataFrame of accounts
        """
        try:
            # The table name is linkedin_accounts from config
            accounts_table = config.LINKEDIN_ACCOUNTS_TABLE_NAME
            data = _self.db.fetch_all(accounts_table)
            
            if not data:
                return pd.DataFrame()
            
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error fetching LinkedIn accounts: {e}")
            st.error(f"Failed to load accounts: {str(e)}")
            return pd.DataFrame()
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a LinkedIn campaign and all associated leads.
        
        Args:
            campaign_id: Campaign ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete associated leads first
            self.db.delete_many(self.leads_table, {'campaign_id': campaign_id})
            
            # Delete the campaign
            self.db.delete(self.campaigns_table, 'campaign_id', campaign_id)
            
            # Clear cache
            st.cache_data.clear()
            
            logger.info(f"Successfully deleted LinkedIn campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {e}")
            st.error(f"Failed to delete campaign: {str(e)}")
            return False

