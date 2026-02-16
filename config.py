import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable Configuration
# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
LEADS_TABLE_NAME = os.getenv('LEADS_TABLE_NAME', 'leads')
CAMPAIGNS_TABLE_NAME = os.getenv('CAMPAIGNS_TABLE_NAME', 'campaign')
EMAIL_SEQUENCE_TABLE_NAME = os.getenv('EMAIL_SEQUENCE_TABLE_NAME', 'email_sequence')
LINKEDIN_CAMPAIGN_TABLE_NAME = os.getenv('LINKEDIN_CAMPAIGN_TABLE_NAME', 'linkedin_campaign')
LINKEDIN_LEADS_TABLE_NAME = os.getenv('LINKEDIN_LEADS_TABLE_NAME', 'linkedin_leads')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Cache Configuration
CACHE_TTL = 300  # 5 minutes
