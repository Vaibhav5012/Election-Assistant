# 🗳️ Election Process Assistant

> An interactive, accessible Streamlit application that demystifies election processes through guided walkthroughs, visual timelines, Q&A chat, quizzes, and fun facts — powered by structured knowledge bases and optional Google Cloud integrations.

---

## ✨ Features

| Mode | Description |
|---|---|
| 📋 **Learn Step-by-Step** | Guided walkthrough of each election phase with expandable cards and progress tracking |
| 📅 **Election Timeline** | Visual phased progress bars showing pre-election → campaign → voting → post-election |
| 💬 **Ask Questions** | Chat interface with session history, keyword routing, and full-text knowledge-base search |
| 🧠 **Quiz Mode** | Randomized multiple-choice questions with instant feedback, scoring, and letter grades |
| 💡 **Did You Know?** | Rotating factual panel with surprising election trivia |

### Additional Capabilities

- 🌙 **Dark / Light Theme** — Sidebar toggle with custom CSS for both modes
- 📖 **Reading Levels** — Beginner (Grade 8 language) and Advanced (technical terms defined inline)
- 🔗 **Shareable URLs** — Current country and mode encoded in query parameters
- 📤 **Session Export** — One-click export of chat history and quiz scores to Google Docs
- 📊 **Usage Analytics** — Optional Google Sheets logging and GA4 event tracking

---

## 🌍 Supported Countries

| Country | Status |
|---|---|
| 🇮🇳 India | Fully detailed — 10 steps, 4 timeline phases, 5 roles, 8 key terms, 10 quiz questions |
| 🇺🇸 USA | Scaffold — extendable with full data |

> **Adding a new country is zero-code:** drop a JSON file in `data/` following the schema and it appears in the sidebar automatically.

---

## 🚀 Quick Start

### 1. Clone & create a virtual environment

```bash
# Linux / macOS
python -m venv venv && source venv/bin/activate

# Windows
python -m venv venv && venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`. No configuration required — all Google integrations are disabled by default.

### 4. Run the test suite

```bash
make test
```

> **71 tests • 88% coverage** — includes unit tests, AppTest integration tests, and mocked Google API tests.

---

## 🔧 Development

```bash
make format   # Auto-format with black
make lint     # PEP 8 check (flake8 + black --check)
make test     # pytest with coverage report
```

All functions use type hints and Google-style docstrings. Maximum function length is 40 lines. Constants are centralized in `config.py`.

---

## ☁️ Google Services Setup (Optional)

All four integrations are independently toggleable and degrade gracefully when credentials are absent.

### Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Fill in the values for the integrations you want:

| Integration | Enable Flag | Required Credentials |
|---|---|---|
| **Google Sheets** (usage logging) | `ENABLE_SHEETS=true` | `GOOGLE_SERVICE_ACCOUNT_PATH`, `GOOGLE_SHEET_ID` |
| **Google Analytics 4** (event tracking) | `ENABLE_ANALYTICS=true` | `GA4_MEASUREMENT_ID` |
| **Google OAuth2** (user login) | `ENABLE_AUTH=true` | `GOOGLE_CLIENT_SECRET_PATH` |
| **Google Drive** (session export) | Requires OAuth login | Uses OAuth credentials |

> All API calls use exponential backoff (3 retries, 2s base delay via `tenacity`). Failures are logged but never crash the app.

---

## 🔒 Security

- All user input is sanitized via `validators.py` — HTML stripping, control character removal, length enforcement (500 chars max)
- Inputs are checked for SQL injection patterns, XSS payloads, and path traversal sequences
- URL query parameters are validated against whitelisted values before use
- JSON data is validated against `data/schema.json` on every load
- No hardcoded secrets — all credentials loaded via `python-dotenv` / `st.secrets`
- All package versions are pinned in `requirements.txt`

---

## ♿ Accessibility

- **WCAG 2.1 AA** color contrast in both light and dark themes
- Semantic heading hierarchy: `st.title()` → `st.header()` → `st.subheader()`
- All form elements have explicit visible labels (no placeholder-only labels)
- Progress bars are paired with descriptive `st.caption()` text for screen readers
- Minimum font size floor of 14px enforced across all custom CSS
- Color is never used as the sole indicator — always paired with icons (✅, ⚠️, ❌)

---

## 📁 Project Structure

```
election_assistant/
├── main.py                  # App entry point — state init, routing, analytics
├── config.py                # Centralized constants, theme CSS, env helpers
├── requirements.txt         # Pinned dependencies
├── Makefile                 # format, lint, test targets
├── .env.example             # Environment variable template
│
├── components/
│   ├── sidebar.py           # Country, mode, reading level, theme, export
│   ├── steps.py             # Step-by-step explorer with progress tracking
│   ├── timeline.py          # Visual phased timeline with random facts
│   ├── chat.py              # Q&A chat with sanitization pipeline
│   ├── quiz.py              # MCQ quiz with shuffled options and grading
│   └── facts.py             # "Did You Know?" rotating panel
│
├── utils/
│   ├── data_loader.py       # Cached JSON loading with schema validation
│   ├── formatter.py         # O(1) keyword router + full-text search
│   ├── validators.py        # Input sanitization & security checks
│   ├── google_services.py   # Sheets, GA4, OAuth2, Drive export
│   └── logger.py            # File + console logging configuration
│
├── data/
│   ├── india.json           # India election data (fully detailed)
│   ├── usa.json             # USA election data (scaffold)
│   └── schema.json          # JSON Schema Draft 7 for validation
│
└── tests/
    ├── conftest.py           # Shared fixtures (mock data, session state, API mocks)
    ├── test_main.py          # App startup & query param routing (AppTest)
    ├── test_components.py    # Component rendering & interaction (AppTest)
    ├── test_data_loader.py   # Load, cache, validate, missing file, bad schema
    ├── test_formatter.py     # Keyword routing, search, formatting, edge cases
    ├── test_validators.py    # Sanitization, XSS, SQLi, path traversal
    └── test_google_services.py  # Sheets, GA4, OAuth, Drive export (mocked)
```

---

## 📜 License

This project is for educational purposes.
