"""Chat interface component for the Q&A mode.

Decomposes the request pipeline into four private functions
to stay within the 40-line-per-function limit:
  1. _sanitize_input   — clean the raw user string
  2. _route_query      — attempt O(1) keyword lookup
  3. _search_fallback  — full-text knowledge-base search
  4. _build_response   — assemble structured response dict
"""

from __future__ import annotations

import streamlit as st

from config import ENABLE_ANALYTICS, MAX_INPUT_LENGTH
from utils.formatter import (
    format_chat_response,
    keyword_router,
    search_knowledge_base,
)
from utils.google_services import track_event
from utils.validators import is_safe_input, sanitize_query


def render_chat(data: dict) -> None:
    """Render the chat interface and handle user queries.

    Args:
        data: The loaded election data dictionary.
    """
    st.header("💬 Ask Questions")
    st.caption(
        f"Ask anything about {data['country']}'s "
        f"{data['election_type']}"
    )

    # Render message history
    _render_history()

    # Chat input
    user_input = st.chat_input(
        "Type your question here...",
        max_chars=MAX_INPUT_LENGTH,
        key="chat_input",
    )

    if user_input:
        _handle_user_message(user_input, data)


def _render_history() -> None:
    """Render all previous messages from session state."""
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                sources_str = ", ".join(msg["sources"])
                st.caption(f"📚 Sources: {sources_str}")


def _handle_user_message(raw: str, data: dict) -> None:
    """Process a new user message through the full pipeline.

    Args:
        raw: The raw user input string.
        data: The loaded election data dictionary.
    """
    # Store user message
    st.session_state["messages"].append(
        {"role": "user", "content": raw}
    )
    with st.chat_message("user"):
        st.markdown(raw)

    # Process and respond
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = _process_query(raw, data)
        st.markdown(response["content"])
        if response.get("sources"):
            sources_str = ", ".join(response["sources"])
            st.caption(f"📚 Sources: {sources_str}")

    # Store assistant response
    st.session_state["messages"].append(response)

    # Fire GA4 event
    _fire_ga4_event(raw, data)


def _process_query(raw: str, data: dict) -> dict:
    """Run the sanitize → route → search → format pipeline.

    Args:
        raw: The raw user input string.
        data: The loaded election data dictionary.

    Returns:
        A structured response dict.
    """
    clean = _sanitize_input(raw)
    routed = _route_query(clean, data)
    if routed:
        return routed
    fallback_content = _search_fallback(clean, data)
    return _build_response(fallback_content, ["Knowledge Base"])


def _sanitize_input(raw: str) -> str:
    """Clean and validate the raw user input.

    Args:
        raw: The raw input string.

    Returns:
        The sanitized string, or a rejection message marker.
    """
    clean = sanitize_query(raw)
    if not is_safe_input(clean):
        return ""
    return clean


def _route_query(clean: str, data: dict) -> dict | None:
    """Attempt O(1) keyword routing.

    Args:
        clean: The sanitized query string.
        data: The loaded election data dictionary.

    Returns:
        A response dict if matched, else ``None``.
    """
    if not clean:
        return format_chat_response(
            "⚠️ Your input was flagged as potentially unsafe. "
            "Please rephrase your question.",
            ["Input Validation"],
        )
    return keyword_router(clean, data)


def _search_fallback(clean: str, data: dict) -> str:
    """Full-text search across the knowledge base.

    Args:
        clean: The sanitized query string.
        data: The loaded election data dictionary.

    Returns:
        A markdown-formatted result string.
    """
    return search_knowledge_base(clean, data)


def _build_response(content: str, sources: list[str]) -> dict:
    """Assemble the structured assistant response.

    Args:
        content: The markdown response body.
        sources: List of source category strings.

    Returns:
        A dict with ``role``, ``content``, and ``sources`` keys.
    """
    return format_chat_response(content, sources)


def _fire_ga4_event(query: str, data: dict) -> None:
    """Fire the GA4 question_asked event if analytics is enabled.

    Args:
        query: The user's query string.
        data: The election data dictionary (for country context).
    """
    if not ENABLE_ANALYTICS:
        return
    js = track_event(
        "question_asked",
        {"query": query[:100], "country": data["country"]},
    )
    st.markdown(js, unsafe_allow_html=True)
