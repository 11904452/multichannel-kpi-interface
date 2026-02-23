# 📧 Multichannel(Email, Linkedin) KPI Dashboards

A production-ready dashboard for managing and analyzing email and LinkedIn campaigns with clean, modular architecture.

## 🚀 Features

- **Dual Platform Support**: Manage both email and LinkedIn campaigns from one interface
- **Real-time Analytics**: Comprehensive KPIs, charts, and performance metrics
- **Campaign Management**: Full CRUD operations for campaigns and leads
- **Advanced Filtering**: Filter by workspace, campaign, date range
- **Clean Architecture**: Modular design with separated concerns
- **Type-Safe**: Comprehensive type hints throughout
- **Error Handling**: Robust error handling with detailed logging
- **Caching**: Optimized performance with Streamlit caching

## 📁 Project Structure

```
email-campaign-dashboard/
├── app.py                          # Main entry point (50 lines!)
├── run_dashboard.py                # Helper script to run dashboard
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
├── core/                           # Core infrastructure
│   ├── database.py                 # Unified Supabase client
│   ├── exceptions.py               # Custom exceptions
│   ├── logger.py                   # Centralized logging
│   └── validators.py               # Input validation
│
├── api/                            # API layer for CRUD operations
│   ├── base.py                     # Base API handler
│   ├── email_api.py                # Email campaign APIs
│   └── linkedin_api.py             # LinkedIn campaign APIs
│
├── email_campaigns/                # Email campaigns module
│   ├── data/
│   │   ├── repository.py           # Data access layer
│   │   └── processor.py            # Data processing
│   ├── components/
│   │   ├── dashboard.py            # Main dashboard
│   │   ├── filters.py              # Filter components
│   │   ├── kpi_cards.py            # KPI displays
│   │   ├── charts.py               # Chart components
│   │   └── sequence_stats.py       # Sequence statistics
│   └── services/
│       └── metrics.py              # Metrics calculation
│
├── linkedin/                       # LinkedIn module
│   ├── data/
│   │   ├── repository.py           # Data access layer
│   │   └── processor.py            # Data processing
│   ├── components/
│   │   ├── dashboard.py            # Main dashboard
│   │   ├── kpi_cards.py            # KPI displays
│   │   └── charts.py               # Chart components
│   └── services/
│       └── metrics.py              # Metrics calculation
│
├── shared/                         # Shared utilities
│   ├── date_utils.py               # Date utilities
│   ├── ui_components.py            # Reusable UI components
│   └── guide.py                    # Help guide
│
├── assets/                         # Static assets
│   └── styles.css                  # Application styles
│
└── tests/                          # Test suite
    └── __init__.py                 # Test package
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Supabase account
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   cd email-campaign-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   # ── Supabase ──────────────────────────────────────────
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key

   # ── Table Names (Email) ───────────────────────────────
   LEADS_TABLE_NAME=leads
   CAMPAIGNS_TABLE_NAME=campaign
   EMAIL_SEQUENCE_TABLE_NAME=email_sequence
   EMAIL_API_KEYS_TABLE_NAME=email_api_keys

   # ── Table Names (LinkedIn) ────────────────────────────
   LINKEDIN_CAMPAIGN_TABLE_NAME=linkedin_campaign
   LINKEDIN_LEADS_TABLE_NAME=linkedin_leads
   LINKEDIN_ACCOUNTS_TABLE_NAME=linkedin_accounts

   # ── Modal Deployment (optional) ───────────────────────
   MODAL_APP_NAME=
   MODAL_SECRET_NAME=                   # Name of Modal secret (required for prod)
   MODAL_ENV=dev                        # 'dev' = local .env | 'prod' = named secret
   MODAL_MIN_CONTAINERS=1
   MODAL_MAX_INPUTS=100
   MODAL_PORT=8000
   ```

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```
   
   Or use the helper script:
   ```bash
   python run_dashboard.py
   ```

## 📊 Usage

### Accessing the Dashboard

1. Open your browser to `http://localhost:8501`
2. Select your platform (Email or LinkedIn) from the sidebar
3. Use filters to narrow down your data
4. Explore KPIs, charts, and detailed tables

### Email Dashboard

- **Workspace Overview**: High-level metrics across all campaigns
- **Campaign Analysis**: Detailed analysis of individual campaigns
- **Sequence Stats**: Email sequence performance
- **Lead Management**: View and filter interested/objection leads

### LinkedIn Dashboard

- **Campaign Metrics**: Connections, messages, replies, InMail stats
- **Lead Analysis**: Status breakdown, seniority levels
- **Top Performers**: Best performing accounts
- **Conversion Funnel**: Visual representation of campaign funnel
- **Campaign Management**: Delete campaigns with confirmation

## 🔌 API Usage

The dashboard includes a comprehensive API layer for programmatic access:

### Email Campaign API

```python
from api.email_api import EmailCampaignAPI

api = EmailCampaignAPI()

# Get all campaigns
response = api.get_campaigns()

# Get specific campaign
campaign = api.get_campaign_by_id("campaign_123")

# Create campaign
new_campaign = api.create_campaign({
    "Name": "Summer Campaign",
    "workspace_name": "Sales"
})

# Update campaign
updated = api.update_campaign("campaign_123", {
    "Name": "Updated Name"
})

# Delete campaign (and associated leads)
result = api.delete_campaign("campaign_123")

# Get leads
leads = api.get_leads(campaign_id="campaign_123")
```

### LinkedIn Campaign API

```python
from api.linkedin_api.py import LinkedInCampaignAPI

api = LinkedInCampaignAPI()

# Get all campaigns
response = api.get_campaigns()

# Delete campaign
result = api.delete_campaign("campaign_456")

# Get leads with filters
leads = api.get_leads(
    campaign_id="campaign_456",
    status="Interested"
)

# Update lead
updated_lead = api.update_lead("lead_789", {
    "Status": "Interested"
})
```

## 🏗️ Architecture

### Design Principles

1. **Separation of Concerns**: Email and LinkedIn logic completely separated
2. **Single Responsibility**: Each module has one clear purpose
3. **DRY (Don't Repeat Yourself)**: Shared utilities in `shared/` module
4. **Type Safety**: Type hints throughout for better IDE support
5. **Error Handling**: Comprehensive try-catch with logging
6. **Caching**: Strategic use of Streamlit caching for performance

### Key Components

- **Core Layer**: Database, logging, validation, exceptions
- **API Layer**: CRUD operations with error handling
- **Data Layer**: Repository pattern for data access
- **Service Layer**: Business logic and calculations
- **Component Layer**: UI components and dashboards

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

## 📝 Configuration

### Cache Settings

Adjust cache TTL in `config.py`:

```python
CACHE_TTL = 300  # 5 minutes
```

### Logging

Configure logging level in `core/logger.py`:

```python
logger = setup_logger(level=logging.INFO)
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Include docstrings (Google style)
4. Handle errors appropriately
5. Update tests for new features

## 📄 License

This project is proprietary software.

## 🆘 Support

For issues or questions:
1. Check the logs in the console
2. Review error messages in the UI
3. Consult the implementation plan in `.gemini/antigravity/brain/`

## 🎯 Roadmap

- [ ] Add unit tests for all modules
- [ ] Implement export functionality (CSV, Excel)
- [ ] Add email notifications for campaign milestones
- [ ] Create admin panel for user management
- [ ] Add A/B testing capabilities
- [ ] Implement campaign templates

---

**Built with ❤️ using Streamlit, Supabase, and Python**
