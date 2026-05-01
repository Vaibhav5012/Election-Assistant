"""Sidebar component for country, mode, reading level, and theme selection.

Renders all sidebar controls and applies theme CSS.  Fires GA4
``mode_selected`` events when the user changes country or mode.
"""

from __future__ import annotations

import streamlit as st

from config import (
    DARK_THEME_CSS,
    ENABLE_ANALYTICS,
    ENABLE_AUTH,
    LIGHT_THEME_CSS,
    MODE_OPTIONS,
    READING_LEVELS,
)
from utils.data_loader import get_available_countries
from utils.google_services import export_session_to_drive, track_event


def render_sidebar() -> tuple[str, str]:
    """Render all sidebar controls and return selected country and mode.

    Returns:
        A tuple of ``(country, mode)`` strings currently selected.
    """
    with st.sidebar:
        st.title("🗳️ Election Assistant")
        st.caption("Learn about elections worldwide")

        # --- Country Selector ---
        countries = get_available_countries()
        country = st.selectbox(
            "Select Country",
            options=countries,
            index=countries.index(st.session_state["country"]),
            format_func=lambda c: c.capitalize(),
            key="sidebar_country",
        )

        # --- Mode Selector ---
        mode = st.radio(
            "Choose Mode",
            options=MODE_OPTIONS,
            index=MODE_OPTIONS.index(st.session_state["mode"]),
            key="sidebar_mode",
        )

        # --- Reading Level Selector ---
        reading_level = st.radio(
            "Reading Level",
            options=READING_LEVELS,
            index=READING_LEVELS.index(
                st.session_state["reading_level"]
            ),
            key="sidebar_reading_level",
            help=(
                "Beginner: plain language. "
                "Advanced: technical terms with definitions."
            ),
        )

        st.divider()

        # --- Theme Toggle ---
        dark_mode = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state["theme"] == "dark",
            key="sidebar_theme",
        )

        st.divider()

        # --- Export Button (OAuth-gated) ---
        _render_export_button()

    # --- Sync to session state and fire GA4 ---
    _sync_state(country, mode, reading_level, dark_mode)
    _apply_theme()

    return country, mode


def _render_export_button() -> None:
    """Show the session export button if OAuth is enabled."""
    if not ENABLE_AUTH:
        return

    if st.button("📤 Export My Session", key="sidebar_export"):
        with st.spinner("Exporting to Google Drive..."):
            link = export_session_to_drive(
                credentials=st.session_state.get("oauth_credentials"),
                chat_history=st.session_state.get("messages", []),
                quiz_score=st.session_state.get("quiz_score", 0),
                quiz_total=len(
                    st.session_state.get("quiz_answers", [])
                ),
            )
        if link:
            st.success(f"[Open your report]({link})")
        else:
            st.warning("Export failed. Please sign in first.")


def _sync_state(
    country: str, mode: str, reading_level: str, dark: bool
) -> None:
    """Persist widget values into session state and fire GA4.

    Args:
        country: Selected country string.
        mode: Selected mode string.
        reading_level: Selected reading level string.
        dark: Whether dark mode is enabled.
    """
    changed = (
        country != st.session_state["country"]
        or mode != st.session_state["mode"]
    )

    st.session_state["country"] = country
    st.session_state["mode"] = mode
    st.session_state["reading_level"] = reading_level
    st.session_state["theme"] = "dark" if dark else "light"

    # Fire GA4 event on change
    if changed and ENABLE_ANALYTICS:
        js = track_event(
            "mode_selected",
            {"country": country, "mode": mode},
        )
        st.markdown(js, unsafe_allow_html=True)


def _apply_theme() -> None:
    """Inject the CSS for the currently selected theme."""
    css = (
        DARK_THEME_CSS
        if st.session_state["theme"] == "dark"
        else LIGHT_THEME_CSS
    )
    st.markdown(css, unsafe_allow_html=True)
