"""Step-by-step election explorer component.

Renders election steps as expandable cards with a progression
button.  Adapts content based on the selected reading level
and fires GA4 ``step_advanced`` events.
"""

from __future__ import annotations

import streamlit as st

from config import ENABLE_ANALYTICS
from utils.formatter import format_step_response
from utils.google_services import track_event


def render_steps(data: dict) -> None:
    """Render the step-by-step election explorer.

    Args:
        data: The loaded election data dictionary.
    """
    steps = data.get("steps", [])
    total = len(steps)
    current = st.session_state["current_step"]
    reading_level = st.session_state["reading_level"]

    st.header("📋 Learn Step-by-Step")
    st.caption(
        f"{data['country']} — {data['election_type']}"
    )

    # --- Progress indicator ---
    completed = len(st.session_state["steps_completed"])
    st.progress(
        completed / total if total else 0,
        text=f"Progress: {completed} of {total} steps completed",
    )

    # --- Step cards ---
    _render_step_cards(steps, current, reading_level)

    # --- Navigation buttons ---
    _render_navigation(steps, current, total, data)


def _render_step_cards(
    steps: list[dict], current: int, reading_level: str
) -> None:
    """Render each step as an expandable card.

    Args:
        steps: List of step dictionaries.
        current: The current step index.
        reading_level: ``"Beginner"`` or ``"Advanced"``.
    """
    for i, step in enumerate(steps):
        # Mark completed steps with a checkmark
        prefix = "✅ " if i in st.session_state["steps_completed"] else ""
        expanded = i == current

        with st.expander(
            f"{prefix}Step {step['id']}: {step['title']}",
            expanded=expanded,
        ):
            content = format_step_response(step, reading_level)
            st.markdown(content)

            # Show "Did You Know?" for the current step
            if step.get("did_you_know"):
                st.info(f"💡 **Did You Know?** {step['did_you_know']}")


def _render_navigation(
    steps: list[dict], current: int, total: int, data: dict
) -> None:
    """Render Previous / Next navigation buttons.

    Args:
        steps: List of step dictionaries.
        current: The current step index.
        total: Total number of steps.
        data: The full election data dict (for GA4 context).
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current > 0:
            if st.button("⬅️ Previous", key="step_prev"):
                st.session_state["current_step"] = current - 1
                st.rerun()

    with col3:
        if current < total - 1:
            if st.button("Next ➡️", key="step_next"):
                _advance_step(current, data)
                st.rerun()

    with col2:
        if current == total - 1:
            st.success("🎉 You've completed all steps!")


def _advance_step(current: int, data: dict) -> None:
    """Advance to the next step and fire GA4 event.

    Args:
        current: The current step index (0-based).
        data: The full election data dict.
    """
    # Mark current step as completed
    st.session_state["steps_completed"].add(current)
    st.session_state["current_step"] = current + 1

    # Fire GA4 event
    if ENABLE_ANALYTICS:
        step_id = data["steps"][current]["id"]
        js = track_event(
            "step_advanced",
            {"step_id": step_id, "country": data["country"]},
        )
        st.markdown(js, unsafe_allow_html=True)
