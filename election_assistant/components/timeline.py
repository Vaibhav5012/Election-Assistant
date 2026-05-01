"""Visual election timeline component.

Renders a phased progress bar with descriptions and a random
"Did You Know?" fact from the current dataset.
"""

from __future__ import annotations

import random

import streamlit as st


def render_timeline(data: dict) -> None:
    """Render the election timeline with phase progress bars.

    Args:
        data: The loaded election data dictionary.
    """
    phases = data.get("timeline", {}).get("phases", [])
    total = len(phases)

    st.header("📅 Election Timeline")
    st.caption(
        f"{data['country']} — {data['election_type']}"
    )

    # --- Phase cards ---
    for i, phase in enumerate(phases):
        _render_phase(phase, i, total)

    # --- Random fact ---
    _render_random_fact(data)


def _render_phase(
    phase: dict, index: int, total: int
) -> None:
    """Render a single timeline phase with a progress bar.

    Args:
        phase: A single phase dictionary.
        index: The zero-based index of this phase.
        total: Total number of phases.
    """
    progress_value = (index + 1) / total
    label = f"Phase {phase['id']} of {total}: {phase['name']}"

    st.subheader(f"Phase {phase['id']}: {phase['name']}")
    st.progress(progress_value, text=label)
    st.caption(f"**Progress:** {label}")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"- {phase['description']}")
    with col2:
        offset_start = phase["start_offset_days"]
        offset_end = phase["end_offset_days"]
        st.metric(
            "Day Range (relative to election)",
            f"{offset_start:+d} to {offset_end:+d}",
        )

    st.divider()


def _render_random_fact(data: dict) -> None:
    """Display a random Did You Know fact from the steps.

    Args:
        data: The loaded election data dictionary.
    """
    facts = [
        step["did_you_know"]
        for step in data.get("steps", [])
        if step.get("did_you_know")
    ]
    if not facts:
        return

    # Use a session-stable random seed so the fact persists
    if "timeline_fact_index" not in st.session_state:
        st.session_state["timeline_fact_index"] = random.randint(
            0, len(facts) - 1
        )
    idx = st.session_state["timeline_fact_index"] % len(facts)

    st.info(f"💡 **Did You Know?** {facts[idx]}")

    if st.button("🔄 New Fact", key="timeline_new_fact"):
        st.session_state["timeline_fact_index"] = (
            (idx + 1) % len(facts)
        )
        st.rerun()
