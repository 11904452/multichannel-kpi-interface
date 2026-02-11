# 📧 Multichannel(Email, Linkedin) KPI Dashboards

A production-ready Python dashboard for monitoring email campaign KPIs, built with Streamlit and Airtable.

## Features
- **Real-time KPI Monitoring**: Track Total Sent, Reply Rates, Bounce Rates, and more.
- **Dynamic Filtering**: Filter by Workspace, Date Range, and Campaign.
- **Interactive Visualizations**: Breakdown of replies, bounces, and ESP distribution.
- **Data Export**: Download campaign performance data as CSV.
- **Mobile Responsive**: Works on various screen sizes.

## 🚀 Local Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Airtable account with API access
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multichannel-kpi-interface
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and add your Airtable credentials:
     ```
     AIRTABLE_API_KEY=your_key_here
     AIRTABLE_BASE_ID=your_base_id_here
     ```

5. **Run the Dashboard**
   ```bash
   streamlit run app.py
   ```
   The app will open at `http://localhost:8501`.

## 🔑 Getting Airtable Credentials

1. **API Key**: 
   - Visit [Airtable Account](https://airtable.com/account).
   - Click "Generate API key" (or use Personal Access Tokens if legacy keys are deprecated).

2. **Base ID**:
   - Open your Airtable Base.
   - Go to `Help > API documentation`.
   - The Base ID is in the URL (e.g., `https://airtable.com/appXXXXXXXXXX/api/docs` -> `appXXXXXXXXXX`).

## 🛠️ Project Structure
```
email-campaign-dashboard/
├── app.py                  # Main application entry point
├── config.py               # Configuration constants
├── .env                    # Secrets (not committed)
├── data/
│   ├── airtable_client.py  # Airtable API handling
│   └── data_processor.py   # Data cleaning
├── components/
│   ├── filters.py          # Sidebar filters
│   ├── kpi_cards.py        # Top metric cards
│   └── charts.py           # Plotly charts
└── utils/
    ├── date_utils.py       # Date helpers
    └── metrics.py          # KPI calculations
```

## ⚠️ Troubleshooting

- **Connection Error**: Check your `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID` in `.env`.
- **Missing Columns**: Ensure your Airtable schema matches the expected table names (`Leads`, `Campaigns`) and field names.
- **Empty Charts**: Check if your Date Range filter matches the data in `created_date` (for Campaigns) or `reply_date` (for Leads).

## 📄 License
[Your License Here]
