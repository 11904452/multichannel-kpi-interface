import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
LEADS_TABLE_NAME = os.getenv('LEADS_TABLE_NAME', 'Leads')
CAMPAIGNS_TABLE_NAME = os.getenv('CAMPAIGNS_TABLE_NAME', 'Campaigns')
EMAIL_SEQUENCE_TABLE_NAME = os.getenv('EMAIL_SEQUENCE_TABLE_NAME')
LINKEDIN_CAMPAIGN_TABLE_NAME = os.getenv('LINKEDIN_CAMPAIGN_TABLE_NAME')
LINKEDIN_LEADS_TABLE_NAME = os.getenv('LINKEDIN_LEADS_TABLE_NAME')

# Cache Configuration
CACHE_TTL = 300  # 5 minutes
