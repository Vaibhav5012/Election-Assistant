"""Centralized configuration and constants for the Election Assistant app.

All magic numbers, strings, and environment-dependent settings live here.
No other module should hardcode these values.
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# --- Load .env file if present ---
load_dotenv()


# --- Path Constants ---
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
SCHEMA_PATH: Path = DATA_DIR / "schema.json"


# --- Application Constants ---
APP_TITLE: str = "Election Assistant"
APP_ICON: str = "🗳️"
MAX_INPUT_LENGTH: int = 500
CACHE_TTL: int = 3600
DEFAULT_COUNTRY: str = "india"
DEFAULT_MODE: str = "Learn Step-by-Step"
DEFAULT_READING_LEVEL: str = "Beginner"

SUPPORTED_COUNTRIES: list[str] = ["india", "usa"]

MODE_OPTIONS: list[str] = [
    "Learn Step-by-Step",
    "Election Timeline",
    "Ask Questions",
    "Quiz Mode",
    "Did You Know?",
]

READING_LEVELS: list[str] = ["Beginner", "Advanced"]


# --- Session State Keys ---
SESSION_KEYS: dict[str, object] = {
    "messages": [],
    "current_step": 0,
    "quiz_score": 0,
    "quiz_index": 0,
    "quiz_answers": [],
    "quiz_shuffled_options": {},
    "steps_completed": set(),
    "theme": "light",
    "reading_level": DEFAULT_READING_LEVEL,
    "country": DEFAULT_COUNTRY,
    "mode": DEFAULT_MODE,
}


# --- Secret / Environment Helper ---
def get_secret(key: str, default: str = "") -> str:
    """Retrieve a secret from st.secrets first, then fall back to os.environ.

    Args:
        key: The secret / environment variable name.
        default: Fallback value if the key is not found anywhere.

    Returns:
        The secret value as a string.
    """
    # Streamlit Cloud secrets take priority
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        pass
    # Fall back to environment variables (loaded from .env via dotenv)
    return os.environ.get(key, default)


# --- Google Service Feature Flags ---
ENABLE_SHEETS: bool = get_secret("ENABLE_SHEETS", "false").lower() == "true"
ENABLE_ANALYTICS: bool = (
    get_secret("ENABLE_ANALYTICS", "false").lower() == "true"
)
ENABLE_AUTH: bool = get_secret("ENABLE_AUTH", "false").lower() == "true"
GA4_MEASUREMENT_ID: str = get_secret("GA4_MEASUREMENT_ID", "")
GOOGLE_SERVICE_ACCOUNT_PATH: str = get_secret(
    "GOOGLE_SERVICE_ACCOUNT_PATH", ""
)
GOOGLE_SHEET_ID: str = get_secret("GOOGLE_SHEET_ID", "")
GOOGLE_CLIENT_SECRET_PATH: str = get_secret("GOOGLE_CLIENT_SECRET_PATH", "")


# --- Theme CSS ---
# NOTE: All font-size values below comply with the WCAG 14px minimum floor.
# The smallest size used is 14px (.source-tag); body text is 16px.
LIGHT_THEME_CSS: str = """
<style>
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #F7F8FA;
        --text-primary: #1A1A2E;
        --text-secondary: #4A4A6A;
        --accent: #3D5AFE;
        --accent-hover: #2541CC;
        --border: #E0E0E0;
        --success: #2E7D32;
        --warning: #F57C00;
        --error: #C62828;
    }
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 16px;
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: var(--text-primary);
    }
    .stApp p, .stApp li, .stApp span {
        font-size: 16px;
        line-height: 1.6;
    }
    .step-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }
    .fact-panel {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        border-left: 4px solid var(--success);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-size: 16px;
    }
    .timeline-phase {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.6rem;
    }
    .source-tag {
        font-size: 14px;
        color: var(--text-secondary);
        font-style: italic;
    }
</style>
"""

# NOTE: All font-size values below comply with the WCAG 14px minimum floor.
DARK_THEME_CSS: str = """
<style>
    :root {
        --bg-primary: #0F0F1A;
        --bg-secondary: #1A1A2E;
        --text-primary: #E8E8F0;
        --text-secondary: #A0A0C0;
        --accent: #7C8CFF;
        --accent-hover: #5A6AE6;
        --border: #2A2A4A;
        --success: #66BB6A;
        --warning: #FFB74D;
        --error: #EF5350;
    }
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 16px;
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: var(--text-primary);
    }
    .stApp p, .stApp li, .stApp span {
        font-size: 16px;
        line-height: 1.6;
    }
    .step-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }
    .fact-panel {
        background: linear-gradient(135deg, #1B3A2A 0%, #1A2E1A 100%);
        border-left: 4px solid var(--success);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-size: 16px;
    }
    .timeline-phase {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.6rem;
    }
    .source-tag {
        font-size: 14px;
        color: var(--text-secondary);
        font-style: italic;
    }
</style>
"""
