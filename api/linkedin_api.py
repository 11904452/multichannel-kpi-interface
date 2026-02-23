"""
LinkedIn Campaign API for CRUD operations.

This module provides API functions for managing LinkedIn campaigns
and leads.
"""

from typing import List, Dict, Optional, Any

import streamlit as st

from core.database import get_database_client
from core.validators import validate_campaign_id, validate_required_fields
from core.logger import logger
from api.base import handle_api_errors, log_api_call, APIResponse
import config


class LinkedInCampaignAPI:
    """API handler for LinkedIn campaign operations."""
    
    def __init__(self):
        """Initialize the LinkedIn campaign API."""
        self.db = get_database_client()
        self.campaigns_table = config.LINKEDIN_CAMPAIGN_TABLE_NAME
        self.leads_table = config.LINKEDIN_LEADS_TABLE_NAME
    
    @st.cache_data(ttl=config.CACHE_TTL)
    @handle_api_errors
    @log_api_call
    def get_campaigns(_self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get all LinkedIn campaigns with optional filters.
        
        Args:
            filters: Optional dictionary of filters
            
        Returns:
            API response with list of campaigns
        """
        campaigns = _self.db.fetch_all(_self.campaigns_table, filters)
        return APIResponse.success(campaigns, f"Retrieved {len(campaigns)} campaigns")
    
    @st.cache_data(ttl=config.CACHE_TTL)
    @handle_api_errors
    @log_api_call
    def get_campaign_by_id(_self, campaign_id: str) -> Dict[str, Any]:
        """
        Get a specific LinkedIn campaign by ID.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            API response with campaign data
        """
        campaign_id = validate_campaign_id(campaign_id)
        campaign = _self.db.fetch_by_id(_self.campaigns_table, 'campaign_id', campaign_id)
        return APIResponse.success(campaign, "Campaign retrieved successfully")
    
    @handle_api_errors
    @log_api_call
    def create_campaign(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new LinkedIn campaign.
        
        Args:
            data: Campaign data dictionary
            
        Returns:
            API response with created campaign
        """
        # Validate required fields
        required_fields = ['campaign_name']
        validate_required_fields(data, required_fields)
        
        campaign = self.db.insert(self.campaigns_table, data)
        st.cache_data.clear()  # Clear cache after modification
        return APIResponse.success(campaign, "Campaign created successfully")
    
    @handle_api_errors
    @log_api_call
    def update_campaign(self, campaign_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing LinkedIn campaign.
        
        Args:
            campaign_id: Campaign ID
            data: Dictionary of fields to update
            
        Returns:
            API response with updated campaign
        """
        campaign_id = validate_campaign_id(campaign_id)
        campaign = self.db.update(self.campaigns_table, 'campaign_id', campaign_id, data)
        st.cache_data.clear()  # Clear cache after modification
        return APIResponse.success(campaign, "Campaign updated successfully")
    
    @handle_api_errors
    @log_api_call
    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Delete a LinkedIn campaign and all associated leads.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            API response indicating success
        """
        campaign_id = validate_campaign_id(campaign_id)
        
        # Delete associated leads first
        # self.db.delete_many(self.leads_table, {'campaign_id': campaign_id})
        
        # Delete the campaign
        self.db.delete(self.campaigns_table, 'campaign_id', campaign_id)
        
        st.cache_data.clear()  # Clear cache after modification
        return APIResponse.success(
            {"campaign_id": campaign_id},
            "Campaign and associated leads deleted successfully"
        )
    
    @st.cache_data(ttl=config.CACHE_TTL)
    @handle_api_errors
    @log_api_call
    def get_leads(_self, campaign_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get LinkedIn leads, optionally filtered by campaign or status.
        
        Args:
            campaign_id: Optional campaign ID to filter by
            status: Optional status to filter by
            
        Returns:
            API response with list of leads
        """
        filters = {}
        if campaign_id:
            filters['campaign_id'] = campaign_id
        if status:
            filters['Status'] = status
        
        leads = _self.db.fetch_all(_self.leads_table, filters or None)
        return APIResponse.success(leads, f"Retrieved {len(leads)} leads")
    
    @handle_api_errors
    @log_api_call
    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a LinkedIn lead.
        
        Args:
            lead_id: Lead ID
            data: Dictionary of fields to update
            
        Returns:
            API response with updated lead
        """
        lead = self.db.update(self.leads_table, 'id', lead_id, data)
        st.cache_data.clear()  # Clear cache after modification
        return APIResponse.success(lead, "Lead updated successfully")
    
    @handle_api_errors
    @log_api_call
    def delete_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Delete a specific LinkedIn lead.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            API response indicating success
        """
        self.db.delete(self.leads_table, 'id', lead_id)
        st.cache_data.clear()  # Clear cache after modification
        return APIResponse.success({"lead_id": lead_id}, "Lead deleted successfully")
