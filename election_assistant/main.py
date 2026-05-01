"""Election Assistant — Application entry point.

Configures the Streamlit page, initializes session state,
validates data on startup, and routes to the selected mode
component.
"""

from __future__ import annotations

import streamlit as st

from config import (
    APP_ICON,
    APP_TITLE,
    ENABLE_ANALYTICS,
    GA4_MEASUREMENT_ID,
    SESSION_KEYS,
)
from utils.logger import get_logger

logger = get_logger(__name__)


# --- Page Configuration (must be the first Streamlit call) ---
st.set_page_config(
    layout="wide",
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Application entry point — initialize state and render."""
    _init_session_state()
    _inject_analytics()
    _sync_query_params_in()

    # Lazy import to avoid circular dependency
    from components.sidebar import render_sidebar

    country, mode = render_sidebar()

    _sync_query_params_out(country, mode)
    _load_and_render(country, mode)


# --- Session State Initialization ---
def _init_session_state() -> None:
    """Initialize all session state keys once using a guard."""
    for key, default in SESSION_KEYS.items():
        if key not in st.session_state:
            # Use a copy for mutable defaults to avoid aliasing
            if isinstance(default, (list, dict, set)):
                st.session_state[key] = type(default)(default)
            else:
                st.session_state[key] = default


# --- GA4 Script Injection ---
def _inject_analytics() -> None:
    """Inject the GA4 tracking script if analytics is enabled."""
    if not ENABLE_ANALYTICS or not GA4_MEASUREMENT_ID:
        return
    from utils.google_services import inject_ga4_script

    ga4_html = inject_ga4_script(GA4_MEASUREMENT_ID)
    st.markdown(ga4_html, unsafe_allow_html=True)


def _sync_query_params_in() -> None:
    """Read URL query params into session state on first load."""
    from config import DEFAULT_COUNTRY, DEFAULT_MODE, MODE_OPTIONS
    from utils.validators import validate_country

    params = st.query_params

    if "country" in params:
        try:
            st.session_state["country"] = validate_country(params["country"])
        except ValueError:
            logger.warning("Invalid country param: %s", params["country"])
            st.session_state["country"] = DEFAULT_COUNTRY

    if "mode" in params:
        mode = params["mode"]
        if mode in MODE_OPTIONS:
            st.session_state["mode"] = mode
        else:
            logger.warning("Invalid mode param: %s", mode)
            st.session_state["mode"] = DEFAULT_MODE


def _sync_query_params_out(country: str, mode: str) -> None:
    """Write current selections back to URL query params.

    Args:
        country: The selected country string.
        mode: The selected mode string.
    """
    st.query_params["country"] = country
    st.query_params["mode"] = mode


# --- Data Loading & Mode Routing ---
def _load_and_render(country: str, mode: str) -> None:
    """Load election data and route to the correct component.

    Args:
        country: The selected country string.
        mode: The selected mode string.
    """
    from utils.data_loader import load_election_data

    try:
        data = load_election_data(country)
    except FileNotFoundError:
        st.error(
            f"⚠️ No data available for **{country.capitalize()}**. "
            "Please select another country."
        )
        logger.error("Data file not found for: %s", country)
        return
    except Exception as exc:
        st.error(
            "⚠️ Failed to load election data. "
            "Please check the data files."
        )
        logger.exception("Data loading failed: %s", exc)
        return

    _route_mode(mode, data)


def _route_mode(mode: str, data: dict) -> None:
    """Route to the correct component based on the selected mode.

    Args:
        mode: The selected mode string.
        data: The loaded election data dictionary.
    """
    if mode == "Learn Step-by-Step":
        from components.steps import render_steps

        render_steps(data)
    elif mode == "Election Timeline":
        from components.timeline import render_timeline

        render_timeline(data)
    elif mode == "Ask Questions":
        from components.chat import render_chat

        render_chat(data)
    elif mode == "Quiz Mode":
        from components.quiz import render_quiz

        render_quiz(data)
    elif mode == "Did You Know?":
        from components.facts import render_facts

        render_facts(data)
    else:
        st.warning(f"Unknown mode: {mode}")


# --- Run ---
if __name__ == "__main__":
    main()
else:
    # Streamlit runs the module directly, not via __main__
    main()
