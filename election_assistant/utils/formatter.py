"""Response formatting and keyword-based query routing.

Provides O(1) keyword routing for common queries and a fallback
full-text search across the election knowledge base.
"""

from __future__ import annotations

from utils.logger import get_logger

logger = get_logger(__name__)


# --- Keyword Router Map Builder ---
def _build_keyword_map(data: dict) -> dict[str, dict]:
    """Build an O(1) lookup dictionary from election data.

    Maps lowercase keywords to structured response dicts containing
    the matched content and its source category.

    Args:
        data: The loaded election data dictionary.

    Returns:
        A dictionary mapping keyword strings to response dicts.
    """
    keyword_map: dict[str, dict] = {}

    # Index key terms by term name and full form
    for term in data.get("key_terms", []):
        key_lower = term["term"].lower()
        full_lower = term["full_form"].lower()
        entry = {
            "content": _format_term(term),
            "sources": ["Key Terms"],
        }
        keyword_map[key_lower] = entry
        keyword_map[full_lower] = entry

    # Index roles by name and abbreviation
    for role in data.get("roles", []):
        name_lower = role["name"].lower()
        abbr_lower = role["abbreviation"].lower()
        entry = {
            "content": _format_role(role),
            "sources": ["Roles"],
        }
        keyword_map[name_lower] = entry
        keyword_map[abbr_lower] = entry

    return keyword_map


def _format_term(term: dict) -> str:
    """Format a key-term dict as a readable markdown string.

    Args:
        term: A single key-term dictionary.

    Returns:
        A markdown-formatted string.
    """
    lines = [
        f"**{term['term']}** — {term['full_form']}",
        f"- {term['definition']}",
    ]
    if "introduced" in term:
        lines.append(f"- *Introduced:* {term['introduced']}")
    return "\n".join(lines)


def _format_role(role: dict) -> str:
    """Format a role dict as a readable markdown string.

    Args:
        role: A single role dictionary.

    Returns:
        A markdown-formatted string.
    """
    lines = [
        f"**{role['name']}** ({role['abbreviation']})",
        f"- {role['description']}",
        "- **Key powers:**",
    ]
    for power in role.get("powers", []):
        lines.append(f"  - {power}")
    return "\n".join(lines)


# --- Public API ---
def keyword_router(query: str, data: dict) -> dict | None:
    """Attempt O(1) keyword lookup for a user query.

    Args:
        query: The sanitized user query string.
        data: The loaded election data dictionary.

    Returns:
        A response dict ``{"content": str, "sources": list}``
        if a match is found, else ``None``.
    """
    keyword_map = _build_keyword_map(data)
    query_lower = query.strip().lower()

    # Direct match
    if query_lower in keyword_map:
        return keyword_map[query_lower]

    # Check if any keyword appears as a substring in the query
    for keyword, response in keyword_map.items():
        if len(keyword) >= 3 and keyword in query_lower:
            return response

    return None


def search_knowledge_base(query: str, data: dict) -> str:
    """Fallback full-text search across steps, roles, and terms.

    Args:
        query: The sanitized user query string.
        data: The loaded election data dictionary.

    Returns:
        A markdown-formatted string with the best matching content,
        or a "no results" message.
    """
    query_lower = query.strip().lower()
    results: list[str] = []

    # Search steps
    results.extend(_search_steps(query_lower, data))
    # Search roles
    results.extend(_search_roles(query_lower, data))
    # Search key terms
    results.extend(_search_terms(query_lower, data))

    if not results:
        return _no_results_message(query)

    return "\n\n---\n\n".join(results[:3])


def _search_steps(query: str, data: dict) -> list[str]:
    """Search election steps for query matches.

    Args:
        query: Lowercased query string.
        data: The election data dictionary.

    Returns:
        List of formatted matching step strings.
    """
    matches = []
    for step in data.get("steps", []):
        searchable = (
            f"{step['title']} {step['description']} "
            f"{' '.join(step.get('key_terms', []))}"
        ).lower()
        if query in searchable or any(
            word in searchable for word in query.split() if len(word) >= 3
        ):
            matches.append(format_step_response(step))
    return matches


def _search_roles(query: str, data: dict) -> list[str]:
    """Search roles for query matches.

    Args:
        query: Lowercased query string.
        data: The election data dictionary.

    Returns:
        List of formatted matching role strings.
    """
    matches = []
    for role in data.get("roles", []):
        searchable = (
            f"{role['name']} {role['abbreviation']} "
            f"{role['description']}"
        ).lower()
        if query in searchable or any(
            word in searchable for word in query.split() if len(word) >= 3
        ):
            matches.append(_format_role(role))
    return matches


def _search_terms(query: str, data: dict) -> list[str]:
    """Search key terms for query matches.

    Args:
        query: Lowercased query string.
        data: The election data dictionary.

    Returns:
        List of formatted matching term strings.
    """
    matches = []
    for term in data.get("key_terms", []):
        searchable = (
            f"{term['term']} {term['full_form']} {term['definition']}"
        ).lower()
        if query in searchable or any(
            word in searchable for word in query.split() if len(word) >= 3
        ):
            matches.append(_format_term(term))
    return matches


def format_step_response(
    step: dict, reading_level: str = "Beginner"
) -> str:
    """Format an election step as a bullet-pointed markdown block.

    Args:
        step: A single step dictionary from the election data.
        reading_level: ``"Beginner"`` or ``"Advanced"``.

    Returns:
        A markdown-formatted string.
    """
    # Choose description based on reading level
    if reading_level == "Beginner" and "description_beginner" in step:
        desc = step["description_beginner"]
    else:
        desc = step["description"]

    lines = [
        f"### Step {step['id']}: {step['title']}",
        f"- {desc}",
        f"- **Duration:** {step['duration']}",
        f"- **Responsible:** {step['responsible_party']}",
    ]
    if step.get("key_terms"):
        terms_str = ", ".join(step["key_terms"])
        lines.append(f"- **Key Terms:** {terms_str}")
    return "\n".join(lines)


def format_chat_response(
    content: str, sources: list[str]
) -> dict:
    """Create a structured assistant response dict.

    Args:
        content: The markdown response body.
        sources: List of source category strings.

    Returns:
        A dict with ``role``, ``content``, and ``sources`` keys.
    """
    return {
        "role": "assistant",
        "content": content,
        "sources": sources,
    }


def _no_results_message(query: str) -> str:
    """Return a friendly 'no results' message.

    Args:
        query: The original user query.

    Returns:
        A markdown string guiding the user to rephrase.
    """
    return (
        f"I couldn't find information about **\"{query}\"** "
        "in the current knowledge base.\n\n"
        "**Try:**\n"
        "- Using specific terms like *EVM*, *VVPAT*, or *MCC*\n"
        "- Asking about a specific election step or role\n"
        "- Checking the **Learn Step-by-Step** mode for a "
        "guided walkthrough"
    )
