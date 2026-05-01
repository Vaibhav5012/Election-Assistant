"""Did You Know? facts panel component.

Displays rotating election facts from the current dataset
with a refresh button to cycle through available facts.
"""

from __future__ import annotations

import random

import streamlit as st


def render_facts(data: dict) -> None:
    """Render the Did You Know? facts panel.

    Args:
        data: The loaded election data dictionary.
    """
    st.header("💡 Did You Know?")
    st.caption(
        f"Surprising facts about {data['country']}'s elections"
    )

    facts = _collect_facts(data)

    if not facts:
        st.info("No facts available for this country yet.")
        return

    # Get or initialize the current fact index
    if "fact_panel_index" not in st.session_state:
        st.session_state["fact_panel_index"] = random.randint(
            0, len(facts) - 1
        )

    idx = st.session_state["fact_panel_index"] % len(facts)
    _display_fact(facts[idx], idx, len(facts))


def _collect_facts(data: dict) -> list[dict]:
    """Collect all facts with their source step titles.

    Args:
        data: The loaded election data dictionary.

    Returns:
        A list of dicts with ``text`` and ``source`` keys.
    """
    facts = []
    for step in data.get("steps", []):
        if step.get("did_you_know"):
            facts.append(
                {
                    "text": step["did_you_know"],
                    "source": step["title"],
                }
            )
    return facts


def _display_fact(
    fact: dict, index: int, total: int
) -> None:
    """Display a single fact card with navigation.

    Args:
        fact: A dict with ``text`` and ``source`` keys.
        index: The current fact index.
        total: Total number of facts available.
    """
    st.info(f"💡 {fact['text']}")
    st.caption(f"📌 From: {fact['source']}")
    st.caption(f"Fact {index + 1} of {total}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous Fact", key="fact_prev"):
            st.session_state["fact_panel_index"] = (
                (index - 1) % total
            )
            st.rerun()
    with col2:
        if st.button("Next Fact ➡️", key="fact_next"):
            st.session_state["fact_panel_index"] = (
                (index + 1) % total
            )
            st.rerun()
