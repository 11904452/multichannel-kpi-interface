from pyairtable import Api
from typing import List, Dict, Optional
import os
import streamlit as st
import config

class AirtableClient:
    """Handles all Airtable API connections and data fetching"""
    
    def __init__(self):
        self.api_key = config.AIRTABLE_API_KEY
        self.base_id = config.AIRTABLE_BASE_ID
        self.leads_table_name = config.LEADS_TABLE_NAME
        self.campaigns_table_name = config.CAMPAIGNS_TABLE_NAME
        self.email_sequence_table_name = config.EMAIL_SEQUENCE_TABLE_NAME
        
        if not self.api_key or not self.base_id:
            st.error("❌ Airtable credentials not found. Please check your .env file.")
            st.stop()
        
        try:
            self.api = Api(self.api_key)
            self.base = self.api.base(self.base_id)
        except Exception as e:
            st.error(f"❌ Failed to initialize Airtable connection: {str(e)}")
            st.stop()
            
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_leads(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch leads with optional Airtable formula filters"""
        try:
            table = _self.base.table(_self.leads_table_name)
            # Fetch all records, respecting formula if provided
            # Note: pyairtable.Table.all() automatically handles pagination
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
            
            # Extract fields from records
            return [record['fields'] for record in records]
        except Exception as e:
            st.error(f"Error fetching leads: {str(e)}")
            return []
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_campaigns(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch campaigns with optional Airtable formula filters"""
        try:
            table = _self.base.table(_self.campaigns_table_name)
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
            return [record['fields'] for record in records]
        except Exception as e:
            st.error(f"Error fetching campaigns: {str(e)}")
            return []

    @st.cache_data(ttl=config.CACHE_TTL)
    def get_email_sequences(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch email sequences with optional Airtable formula filters"""
        try:
            if not _self.email_sequence_table_name:
                return []
                
            table = _self.base.table(_self.email_sequence_table_name)
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
            return [record['fields'] for record in records]
        except Exception as e:
            st.error(f"Error fetching email sequences: {str(e)}")
            return []

    @st.cache_data(ttl=config.CACHE_TTL)
    def get_linkedin_campaigns(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch linkedin campaigns with optional Airtable formula filters"""
        try:
            if not config.LINKEDIN_CAMPAIGN_TABLE_NAME:
                st.warning("Linkedin campaign table name not configured.")
                return []
                
            table = _self.base.table(config.LINKEDIN_CAMPAIGN_TABLE_NAME)
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
            
            # Return full records to preserve createdTime and id if needed
            # But converting to fields + id/createdTime matches existing pattern in dashboard
            processed = []
            for r in records:
                fields = r['fields']
                fields['_id'] = r['id']
                fields['_createdTime'] = r['createdTime']
                processed.append(fields)
            return processed
            
        except Exception as e:
            st.error(f"Error fetching linkedin campaigns: {str(e)}")
            return []

    @st.cache_data(ttl=config.CACHE_TTL)
    def get_linkedin_leads(_self, formula: Optional[str] = None) -> List[Dict]:
        """Fetch linkedin leads with optional Airtable formula filters"""
        try:
            if not config.LINKEDIN_LEADS_TABLE_NAME:
                st.warning("Linkedin leads table name not configured.")
                return []
                
            table = _self.base.table(config.LINKEDIN_LEADS_TABLE_NAME)
            if formula:
                records = table.all(formula=formula)
            else:
                records = table.all()
            
            # Flatten structure similar to mock data requirement if needed, 
            # OR just return fields. Mock data had 'id' and 'createdTime' outside fields.
            processed = []
            for r in records:
                 fields = r['fields']
                 fields['id'] = r['id']
                 fields['createdTime'] = r['createdTime']
                 processed.append(fields)
            return processed

        except Exception as e:
            st.error(f"Error fetching linkedin leads: {str(e)}")
            return []
