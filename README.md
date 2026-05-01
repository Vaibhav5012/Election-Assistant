# 🗳️ Election Process Assistant

An interactive Streamlit web application that helps users understand election processes, timelines, roles, and key concepts through structured, accessible UI components.

## Features

- **Learn Step-by-Step** — Guided walkthrough of each election phase
- **Election Timeline** — Visual staged progress bar with phase details
- **Ask Questions** — Chat interface with session history and knowledge-base Q&A
- **Quiz Mode** — Multiple-choice questions with scoring and feedback
- **Did You Know?** — Rotating factual panel with surprising election facts
- **Dark/Light Mode** — Sidebar toggle for theme preference
- **Reading Levels** — Beginner (Grade 8) and Advanced modes
- **Google Integrations** — Optional Sheets analytics, GA4 tracking, OAuth login, Drive export

## Supported Countries

- 🇮🇳 India (fully detailed)
- 🇺🇸 USA (scaffold, extendable)
- Add new countries by dropping a JSON file in `data/` — no code changes needed.

## Setup

1. **Clone the repo and create a virtual environment:**
   ```bash
   python -m venv venv && source venv/bin/activate   # Linux/Mac
   python -m venv venv && venv\Scripts\activate       # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your Google credentials (optional — app works without them)
   ```

4. **Run the app:**
   ```bash
   streamlit run main.py
   ```

5. **Run tests:**
   ```bash
   make test
   ```

## Google Services Setup (Optional)

All Google integrations are disabled by default. The app is fully functional without them.

1. Create a Google Cloud project and enable Sheets API, Drive API, and Analytics.
2. Download the service account JSON and set `GOOGLE_SERVICE_ACCOUNT_PATH` in `.env`.
3. Set `GOOGLE_SHEET_ID`, `GA4_MEASUREMENT_ID` in `.env`.
4. Set `ENABLE_SHEETS=true`, `ENABLE_ANALYTICS=true`, `ENABLE_AUTH=true` as desired.

## Development

```bash
make format   # Auto-format code with black
make lint     # Check PEP 8 compliance (flake8 + black)
make test     # Run tests with coverage report
```

## Project Structure

```
election_assistant/
├── main.py                  # App entry point
├── config.py                # Centralized config/constants
├── requirements.txt         # Pinned dependencies
├── .env.example             # Environment variable template
├── components/
│   ├── sidebar.py           # Country, mode, reading level selectors
│   ├── chat.py              # Q&A chat interface
│   ├── timeline.py          # Visual election timeline
│   ├── steps.py             # Step-by-step explorer
│   ├── quiz.py              # MCQ quiz component
│   └── facts.py             # "Did You Know?" panel
├── utils/
│   ├── data_loader.py       # Load/validate structured data
│   ├── formatter.py         # Format responses for display
│   ├── logger.py            # Centralized logging
│   ├── validators.py        # Input sanitization & validation
│   └── google_services.py   # Google Sheets, Analytics, OAuth2
├── data/
│   ├── india.json           # India election data
│   ├── usa.json             # USA election data
│   └── schema.json          # JSON schema for validation
└── tests/
    ├── conftest.py           # Shared pytest fixtures
    ├── test_data_loader.py
    ├── test_formatter.py
    ├── test_validators.py
    ├── test_components.py
    └── test_google_services.py
```
