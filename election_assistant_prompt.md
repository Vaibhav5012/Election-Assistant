# 🗳️ Election Process Assistant — Master Engineering Prompt
### For Claude Opus 4.6 | AI-Evaluator Optimized | Production-Grade

---

## 🎯 MISSION

Build a production-ready, interactive **Election Process Assistant** as a Streamlit web application. This tool helps users understand election processes, timelines, roles, and key concepts through structured, interactive, and accessible UI components. The output will be evaluated by an AI agent on code quality, security, efficiency, testing, accessibility, and Google Services integration.

---

## 📁 FILE STRUCTURE (MANDATORY)

```
election_assistant/
│
├── main.py                          # App entry point
├── requirements.txt                 # All dependencies with pinned versions
├── .env.example                     # Template for environment variables (no secrets)
├── config.py                        # Centralized config/constants
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py                   # Country selector, mode selector
│   ├── chat.py                      # Q&A chat interface
│   ├── timeline.py                  # Visual election timeline
│   ├── steps.py                     # Step-by-step explorer
│   ├── quiz.py                      # MCQ quiz component
│   └── facts.py                     # "Did You Know?" panel
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py               # Load/validate structured data
│   ├── formatter.py                 # Format responses for display
│   ├── logger.py                    # Centralized logging
│   ├── validators.py                # Input sanitization & validation
│   └── google_services.py           # Google Sheets, Analytics, OAuth2 integration
│
├── data/
│   ├── india.json                   # India election data
│   ├── usa.json                     # USA election data (extendable)
│   └── schema.json                  # JSON schema for data validation
│
└── tests/
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_formatter.py
    ├── test_validators.py
    ├── test_components.py
    └── conftest.py                  # Shared pytest fixtures
```

---

## 🔧 1. CORE FUNCTIONALITY

### Modes (Sidebar-Selectable)
- **Learn Step-by-Step** — Guided walkthrough of each election phase with expandable cards and a "Next Step" progression button.
- **Election Timeline** — Visual staged progress bar showing Pre-election → Campaign → Voting → Post-election phases with date ranges.
- **Ask Questions** — Chat interface with session history; AI-powered Q&A using structured knowledge base. Must maintain full conversation context within session.
- **Quiz Mode** *(Bonus)* — Multiple-choice questions on election concepts with scoring and feedback.
- **Did You Know?** *(Bonus)* — Rotating factual panel with surprising election facts.

### Countries Supported
- India (default, fully detailed)
- USA (partial scaffold, extendable)
- Architecture must support adding new countries without code changes — only new JSON files.

---

## 🎨 2. UI/UX REQUIREMENTS (STREAMLIT)

### Layout
```python
# Use Streamlit layout primitives exclusively:
st.set_page_config(layout="wide", page_title="Election Assistant", page_icon="🗳️")
st.sidebar.*        # Country selector, mode selector, dark/light toggle
st.container()      # Section grouping
st.columns()        # Responsive side-by-side panels
st.expander()       # Collapsible step cards
st.progress()       # Timeline visual
st.session_state    # Chat history, current step index, quiz state, theme
```

### Design Principles
- **No walls of text.** Every response must use bullet points, numbered steps, or expander cards.
- **Visual hierarchy:** Use `st.header()`, `st.subheader()`, `st.caption()` for clear section differentiation.
- **Highlight key terms** using Streamlit markdown bold or color-coded `st.metric()` boxes.
- **Emoji used sparingly** as section identifiers (max 1 per heading), never decoratively inline.
- **Dark/Light mode toggle** in sidebar using `st.session_state["theme"]` and injected CSS via `st.markdown(<style>)`.

### Chat Interface
- Render previous messages from `st.session_state["messages"]` using `st.chat_message()`.
- Use `st.chat_input()` for user input.
- Each assistant reply is a structured dict: `{"role": "assistant", "content": str, "sources": list}`.
- Show a spinner (`st.spinner()`) during response generation.

---

## 💻 3. CODE QUALITY STANDARDS

### Style & Structure
- **PEP 8 compliant** throughout. Use `black` formatter and `flake8` linter (include in `requirements.txt`).
- **Type hints on every function signature** — parameters and return types.
- **Docstrings on every function and class** using Google-style format:
  ```python
  def load_election_data(country: str) -> dict:
      """Load and validate election data for a given country.

      Args:
          country: ISO country name string (e.g., "india").

      Returns:
          Validated dictionary containing election steps, timeline, roles, and terms.

      Raises:
          FileNotFoundError: If the country JSON file does not exist.
          ValidationError: If the JSON fails schema validation.
      """
  ```
- **No magic numbers or strings.** All constants live in `config.py`.
- **Max function length: 40 lines.** Break larger logic into helpers.
- **Single Responsibility Principle** — each module does exactly one thing.
- **No circular imports.** Use dependency injection or lazy loading where needed.

### Naming Conventions
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Classes: `PascalCase`
- Files: `snake_case.py`

---

## 🔒 4. SECURITY REQUIREMENTS

### Input Handling
- **Sanitize all user input** before processing using a dedicated `validators.py` module:
  ```python
  def sanitize_query(user_input: str) -> str:
      """Strip HTML tags, limit length, and remove control characters."""
  ```
- **Max input length:** 500 characters — enforce in both frontend (`st.chat_input(max_chars=500)`) and backend validation.
- **Reject inputs** containing script tags, SQL injection patterns, or path traversal sequences (`../`).

### Environment & Secrets
- **Never hardcode credentials.** All API keys (Google, etc.) must be loaded via `python-dotenv` from a `.env` file that is listed in `.gitignore`.
- Provide `.env.example` with placeholder values and documentation for each variable.
- Use `st.secrets` for Streamlit Cloud deployment compatibility.

### Data Integrity
- **Validate all JSON data** against `data/schema.json` using `jsonschema` on startup.
- Log validation failures with full traceback to the centralized logger — never swallow exceptions silently.
- Rate-limit Google API calls using exponential backoff (`tenacity` library).

### Dependency Security
- Pin all package versions in `requirements.txt`.
- Include only necessary packages — no unused imports anywhere in the codebase.

---

## ⚡ 5. EFFICIENCY REQUIREMENTS

### Caching
- Use `@st.cache_data` on all data-loading functions to prevent re-reading JSON on every rerender:
  ```python
  @st.cache_data(ttl=3600)
  def load_election_data(country: str) -> dict:
      ...
  ```
- Use `@st.cache_resource` for expensive singleton objects (e.g., Google API clients).

### Session State
- Initialize all session state keys once in `main.py` using a guard pattern:
  ```python
  if "messages" not in st.session_state:
      st.session_state["messages"] = []
  ```
- Never store large objects in session state — store indices or keys, load data on demand.

### Lazy Loading
- Load country data only when selected — not all countries on startup.
- Import heavy modules inside functions where used, not at module level, unless shared.

### Response Generation
- Prefer dictionary-lookup based responses over string matching for common queries — O(1) vs O(n).
- Implement a simple keyword router in `utils/formatter.py` to match query intent before falling back to the knowledge base scan.

---

## ✅ 6. TESTING REQUIREMENTS

Use `pytest` with `pytest-cov` for coverage reporting. Target **≥ 80% coverage**.

### Test Structure
```
tests/
├── conftest.py           # Shared fixtures (mock data, mock session state)
├── test_data_loader.py   # Test load, cache, validate, missing file, bad schema
├── test_formatter.py     # Test response formatting, keyword routing, edge cases
├── test_validators.py    # Test sanitization, length limits, injection patterns
├── test_components.py    # Test component logic (quiz scoring, step progression)
```

### Test Cases (Mandatory)
- **Data Loader:** Valid load, file not found, schema validation failure, malformed JSON.
- **Formatter:** Empty input, special characters, very long strings, known keywords.
- **Validators:** SQL injection attempt, XSS payload, max length exceeded, normal input.
- **Quiz:** Correct answer, wrong answer, all questions answered, score calculation.
- **Timeline:** Correct phase count, correct ordering, boundary phase values.

### Running Tests
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing -v
```

Include a `Makefile` with:
```makefile
test:
    pytest tests/ --cov=. --cov-report=term-missing -v

lint:
    flake8 . --max-line-length=88
    black --check .

format:
    black .
```

---

## ♿ 7. ACCESSIBILITY REQUIREMENTS

### WCAG 2.1 AA Compliance
- **Color contrast:** All text must meet minimum 4.5:1 contrast ratio against its background in both light and dark mode.
- **Never use color alone** to convey meaning — pair colors with icons, labels, or patterns (e.g., ✅ for success, ⚠️ for warning).
- **Alt-text equivalent:** For all `st.image()` calls, include a descriptive `caption` parameter.

### Keyboard Navigation
- Streamlit's native widgets are keyboard-navigable by default — do not override tab order or disable focus styles.
- Ensure all interactive elements (buttons, inputs, expanders) are reachable and operable via keyboard alone.

### Readable Content
- **Reading level:** Write all UI copy at a Grade 8 level or below for beginner mode. Advanced mode may use technical terms but must define them inline on first use.
- **Font size:** Never inject CSS that sets font size below 14px.
- **Line length:** Cap text blocks at 75 characters per line (use `st.columns([2,1])` to constrain prose width).

### Screen Reader Compatibility
- Use semantic heading hierarchy: one `st.title()` per page, then `st.header()`, then `st.subheader()`.
- Label all form elements explicitly — do not rely on placeholder text as the only label.
- `st.progress()` bars must be accompanied by a text description of the current value (e.g., `"Phase 2 of 4: Campaign Period"`).

---

## 🔗 8. GOOGLE SERVICES INTEGRATION

Implement a `utils/google_services.py` module with the following integrations. Each must be **independently toggleable** via `.env` flags (e.g., `ENABLE_SHEETS=true`).

### A. Google Sheets — Usage Analytics
```python
class GoogleSheetsLogger:
    """Logs user query events and quiz results to a Google Sheet for analytics."""

    def log_query(self, country: str, mode: str, query: str, timestamp: str) -> None:
        """Append a query record to the analytics sheet."""

    def log_quiz_result(self, country: str, score: int, total: int) -> None:
        """Append a quiz completion record."""
```
- Auth via **Service Account JSON** (path set in `.env` as `GOOGLE_SERVICE_ACCOUNT_PATH`).
- Sheet ID set via `.env` as `GOOGLE_SHEET_ID`.
- Wrap every write in try/except with exponential backoff (3 retries, 2s base delay).

### B. Google Analytics 4 — Page & Event Tracking
- Inject GA4 measurement script into Streamlit via `st.markdown()` with `unsafe_allow_html=True`:
  ```html
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
  ```
- Track custom events: `mode_selected`, `step_advanced`, `quiz_completed`, `question_asked`.
- `GA4_MEASUREMENT_ID` loaded from `.env`.

### C. Google OAuth2 — Optional User Authentication
- Implement an **optional** login flow using `google-auth-oauthlib`:
  ```python
  def get_oauth_credentials() -> Credentials | None:
      """Return OAuth2 credentials if the user is logged in, else None."""
  ```
- When logged in, personalize the greeting and persist quiz scores to the user's Sheets row.
- OAuth client config loaded from `GOOGLE_CLIENT_SECRET_PATH` in `.env`.
- **Gate this behind `ENABLE_AUTH=true`** — app must be fully functional without auth.

### D. Google Drive — Export Feature
- Add an "Export My Session" button in the sidebar that:
  1. Formats the current chat history and quiz scores as a structured report.
  2. Uploads it as a Google Doc to the user's Drive (requires OAuth login).
  3. Returns and displays the shareable Doc link.

### Integration Contracts
- All Google service calls must be **non-blocking** to the UI — use `st.spinner()` during calls.
- All Google features must **degrade gracefully** when credentials are absent or calls fail — the app must never crash due to a Google API error.
- Log all API errors to the centralized logger with full context.

---

## 📊 9. DATA STRUCTURE (JSON Schema)

### `data/india.json` — Required Fields
```json
{
  "country": "India",
  "election_type": "General Election (Lok Sabha)",
  "steps": [
    {
      "id": 1,
      "title": "Announcement of Elections",
      "description": "The Election Commission of India announces the election schedule.",
      "duration": "1 day",
      "responsible_party": "Election Commission of India",
      "key_terms": ["Model Code of Conduct", "Schedule"],
      "did_you_know": "India's election schedule is one of the most complex logistical operations in the world."
    }
  ],
  "timeline": {
    "phases": [
      {
        "id": 1,
        "name": "Pre-Election Phase",
        "start_offset_days": -90,
        "end_offset_days": -30,
        "color": "#1f77b4",
        "description": "Voter registration, delimitation, and candidate preparation."
      }
    ]
  },
  "roles": [
    {
      "name": "Election Commission of India",
      "abbreviation": "ECI",
      "description": "The constitutional body responsible for administering election processes.",
      "powers": ["Issue Model Code of Conduct", "Deploy security forces", "Cancel elections in specific constituencies"]
    }
  ],
  "key_terms": [
    {
      "term": "EVM",
      "full_form": "Electronic Voting Machine",
      "definition": "A standalone electronic device used to cast votes in Indian elections.",
      "introduced": 1982
    }
  ],
  "quiz": [
    {
      "id": 1,
      "question": "Which body conducts general elections in India?",
      "options": ["Supreme Court", "Election Commission of India", "Parliament", "President's Office"],
      "correct_index": 1,
      "explanation": "The Election Commission of India (ECI) is an autonomous constitutional authority responsible for administering election processes."
    }
  ]
}
```

### `data/schema.json` — Validation Schema
Provide a complete `jsonschema` Draft 7 schema validating all required fields, types, and constraints in the above structure.

---

## 🎁 10. BONUS FEATURES (ALL REQUIRED FOR FULL EVALUATION SCORE)

| Feature | Implementation |
|---|---|
| **Quiz MCQ** | Randomized order, immediate feedback, final score with percentage |
| **Progress Tracking** | `st.session_state` tracks steps completed and quiz score across mode switches |
| **Dark/Light Toggle** | Sidebar toggle injects custom CSS via `st.markdown()` to override Streamlit theme |
| **"Did You Know?" Panel** | Rotates facts per step; shows a random fact on the timeline view |
| **Export to Google Doc** | One-click session export via Google Drive API |
| **Shareable URL State** | Encode current country + mode into URL query params using `st.query_params` |

---

## 📦 11. REQUIREMENTS.TXT (PINNED)

```
streamlit==1.35.0
python-dotenv==1.0.1
jsonschema==4.22.0
google-auth==2.29.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.130.0
tenacity==8.3.0
pytest==8.2.2
pytest-cov==5.0.0
black==24.4.2
flake8==7.1.0
```

---

## 🚀 12. SETUP & RUN INSTRUCTIONS

The generated code must include a `README.md` with:

```markdown
## Setup

1. Clone the repo and create a virtual environment:
   python -m venv venv && source venv/bin/activate

2. Install dependencies:
   pip install -r requirements.txt

3. Configure environment:
   cp .env.example .env
   # Edit .env with your Google credentials (optional — app works without them)

4. Run the app:
   streamlit run main.py

5. Run tests:
   make test

## Google Services Setup (Optional)
- Create a Google Cloud project and enable Sheets API, Drive API, and Analytics.
- Download service account JSON and set GOOGLE_SERVICE_ACCOUNT_PATH in .env.
- Set GOOGLE_SHEET_ID, GA4_MEASUREMENT_ID in .env.
- Set ENABLE_SHEETS=true, ENABLE_AUTH=true as desired.
```

---

## 🤖 13. AI EVALUATOR CHECKLIST

The generated code will be automatically evaluated on the following criteria. Every item must pass:

### Code Quality
- [ ] PEP 8 compliant (passes `flake8` with zero errors)
- [ ] All functions have type hints and Google-style docstrings
- [ ] No function exceeds 40 lines
- [ ] No magic numbers/strings — all constants in `config.py`
- [ ] Modular file structure exactly matches the required layout

### Security
- [ ] All user input sanitized before use
- [ ] No hardcoded secrets anywhere in the codebase
- [ ] `.env.example` provided, `.gitignore` includes `.env`
- [ ] JSON data validated against schema on startup
- [ ] API calls wrapped with error handling and retry logic

### Efficiency
- [ ] All data-loading functions decorated with `@st.cache_data`
- [ ] Session state initialized once with guard pattern
- [ ] No redundant imports or unused variables
- [ ] Keyword routing used before full knowledge-base scan

### Testing
- [ ] `pytest` suite exists with ≥ 80% coverage
- [ ] Tests cover all edge cases listed in Section 6
- [ ] `conftest.py` provides shared fixtures
- [ ] `make test` runs all tests and prints coverage report

### Accessibility
- [ ] WCAG 2.1 AA color contrast in both themes
- [ ] Semantic heading hierarchy respected
- [ ] Progress bars include descriptive text labels
- [ ] No font sizes below 14px injected via custom CSS

### Google Services
- [ ] `google_services.py` implements all four integrations
- [ ] Each integration is togglable via `.env` flag
- [ ] All Google calls are non-blocking and fail gracefully
- [ ] OAuth flow works end-to-end when `ENABLE_AUTH=true`

---

## ⚠️ FINAL NOTES FOR CODE GENERATION

1. **Generate complete, runnable code** — no `...` placeholders, no `# TODO` comments left unimplemented.
2. **Every file in the structure must be generated** in full.
3. **The app must run successfully** with `streamlit run main.py` after `pip install -r requirements.txt`.
4. **Google integrations must be truly optional** — the app must be fully functional when all `ENABLE_*` flags are `false` or `.env` is absent.
5. **The quiz, timeline, and chat must all work offline** using only the JSON data files.
6. **Comment density:** Every non-obvious line of logic should have an inline comment. Every function must have a docstring. Section blocks should have a `# --- Section Name ---` banner comment.
