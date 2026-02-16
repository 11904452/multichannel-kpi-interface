from supabase import create_client, Client
from typing import List, Dict, Optional
import os
import streamlit as st
import config

class SupabaseClient:
    """Handles all Supabase API connections and data fetching"""
    
    def __init__(self):
        self.url = config.SUPABASE_URL
        self.key = config.SUPABASE_KEY
        self.leads_table_name = config.LEADS_TABLE_NAME
        self.campaigns_table_name = config.CAMPAIGNS_TABLE_NAME
        self.email_sequence_table_name = config.EMAIL_SEQUENCE_TABLE_NAME
        
        if not self.url or not self.key:
            st.error("❌ Supabase credentials not found. Please check your .env file.")
            st.stop()
        
        try:
            self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            st.error(f"❌ Failed to initialize Supabase connection: {str(e)}")
            st.stop()
            
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_leads(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch leads"""
        try:
            # Note: formula support in Supabase via postgrest filter if needed, 
            # but for now we fetch all or specific range. 
            # Mirroring Airtable existing behavior of fetching all for now in dashboard context
            response = _self.client.table(_self.leads_table_name).select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching leads: {str(e)}")
            return []
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_campaigns(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch campaigns"""
        try:
            response = _self.client.table(_self.campaigns_table_name).select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching campaigns: {str(e)}")
            return []

    @st.cache_data(ttl=config.CACHE_TTL)
    def get_email_sequences(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch email sequences"""
        try:
            if not _self.email_sequence_table_name:
                return []
                
            response = _self.client.table(_self.email_sequence_table_name).select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching email sequences: {str(e)}")
            return []

    @st.cache_data(ttl=config.CACHE_TTL)
    def get_linkedin_campaigns(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch linkedin campaigns"""
        try:
            if not config.LINKEDIN_CAMPAIGN_TABLE_NAME:
                # st.warning("Linkedin campaign table name not configured.")
                return []
                
            response = _self.client.table(config.LINKEDIN_CAMPAIGN_TABLE_NAME).select("*").execute()
            
            # Normalize to match Airtable output structure if needed (id, created_at)
            # Supabase usually returns these as columns in 'data' dictionary already.
            return response.data
            
        except Exception as e:
            st.error(f"Error fetching linkedin campaigns: {str(e)}")
            return []

    @st.cache_data(ttl=config.CACHE_TTL)
    def get_linkedin_leads(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch linkedin leads"""
        try:
            if not config.LINKEDIN_LEADS_TABLE_NAME:
                # st.warning("Linkedin leads table name not configured.")
                return []
                
            response = _self.client.table(config.LINKEDIN_LEADS_TABLE_NAME).select("*").execute()
            return response.data

        except Exception as e:
            st.error(f"Error fetching linkedin leads: {str(e)}")
            return []

    def delete_linkedin_campaign(self, campaign_id: str) -> bool:
        """
        Delete a linkedin campaign and all its associated leads.
        Returns True if successful, False otherwise.
        """
        try:
            # 1. Delete associated leads first to maintain referential integrity (if enforced, or just for cleanliness)
            # using 'campaign_id' column in leads table
            if not config.LINKEDIN_LEADS_TABLE_NAME or not config.LINKEDIN_CAMPAIGN_TABLE_NAME:
                st.error("Table names not configured.")
                return False

            # Delete leads
            self.client.table(config.LINKEDIN_LEADS_TABLE_NAME).delete().eq("campaign_id", campaign_id).execute()
            
            # 2. Delete the campaign itself
            self.client.table(config.LINKEDIN_CAMPAIGN_TABLE_NAME).delete().eq("campaign_id", campaign_id).execute()
            
            return True
            
        except Exception as e:
            st.error(f"Error deleting campaign {campaign_id}: {str(e)}")
            return False
