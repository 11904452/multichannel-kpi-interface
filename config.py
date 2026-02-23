import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable Configuration
# Airtable Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
LEADS_TABLE_NAME = os.getenv('LEADS_TABLE_NAME')
CAMPAIGNS_TABLE_NAME = os.getenv('CAMPAIGNS_TABLE_NAME')
EMAIL_SEQUENCE_TABLE_NAME = os.getenv('EMAIL_SEQUENCE_TABLE_NAME')
LINKEDIN_CAMPAIGN_TABLE_NAME = os.getenv('LINKEDIN_CAMPAIGN_TABLE_NAME')
LINKEDIN_LEADS_TABLE_NAME = os.getenv('LINKEDIN_LEADS_TABLE_NAME')
LINKEDIN_ACCOUNTS_TABLE_NAME = os.getenv('LINKEDIN_ACCOUNTS_TABLE_NAME')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
EMAIL_API_KEYS_TABLE_NAME = os.getenv('EMAIL_API_KEYS_TABLE_NAME')

APP_NAME        = os.getenv("MODAL_APP_NAME", "")
SECRET_NAME     = os.getenv("MODAL_SECRET_NAME", "")          # Required for prod
MODAL_ENV       = os.getenv("MODAL_ENV", "dev")       # 'dev' | 'prod'
MIN_CONTAINERS  = int(os.getenv("MODAL_MIN_CONTAINERS", "1"))
MAX_INPUTS      = int(os.getenv("MODAL_MAX_INPUTS", "100"))
PORT            = int(os.getenv("MODAL_PORT", "8000"))

# Cache Configuration
CACHE_TTL = 300  # 5 minutes
