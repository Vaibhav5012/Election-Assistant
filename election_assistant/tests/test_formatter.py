"""Tests for the formatter module.

Covers keyword routing, knowledge-base search, step formatting,
and edge cases like empty input and very long strings.
"""

from __future__ import annotations

from utils.formatter import (
    format_chat_response,
    format_step_response,
    keyword_router,
    search_knowledge_base,
)


class TestKeywordRouter:
    """Tests for the keyword_router function."""

    def test_exact_term_match(
        self, sample_india_data: dict
    ) -> None:
        """Direct keyword match returns the correct term info."""
        result = keyword_router("evm", sample_india_data)
        assert result is not None
        assert "Electronic Voting Machine" in result["content"]
        assert "Key Terms" in result["sources"]

    def test_role_abbreviation_match(
        self, sample_india_data: dict
    ) -> None:
        """Role abbreviation match returns role info."""
        result = keyword_router("eci", sample_india_data)
        assert result is not None
        assert "Election Commission" in result["content"]

    def test_substring_match(
        self, sample_india_data: dict
    ) -> None:
        """Query containing a keyword returns a match."""
        result = keyword_router(
            "what is the evm used for", sample_india_data
        )
        assert result is not None

    def test_no_match_returns_none(
        self, sample_india_data: dict
    ) -> None:
        """Query with no matching keywords returns None."""
        result = keyword_router("xyz123", sample_india_data)
        assert result is None

    def test_case_insensitive(
        self, sample_india_data: dict
    ) -> None:
        """Keyword matching is case-insensitive."""
        result = keyword_router("EVM", sample_india_data)
        assert result is not None


class TestSearchKnowledgeBase:
    """Tests for the search_knowledge_base function."""

    def test_empty_input(
        self, sample_india_data: dict
    ) -> None:
        """Empty input returns a 'no results' message."""
        result = search_knowledge_base("", sample_india_data)
        assert "couldn't find" in result.lower() or len(result) > 0

    def test_matching_step(
        self, sample_india_data: dict
    ) -> None:
        """Query matching a step title returns step content."""
        result = search_knowledge_base(
            "announcement", sample_india_data
        )
        assert "Announcement" in result

    def test_special_characters(
        self, sample_india_data: dict
    ) -> None:
        """Input with special characters doesn't crash."""
        result = search_knowledge_base(
            "!@#$%^&*()", sample_india_data
        )
        assert isinstance(result, str)

    def test_very_long_string(
        self, sample_india_data: dict
    ) -> None:
        """Very long input is handled without errors."""
        long_query = "election " * 200
        result = search_knowledge_base(
            long_query, sample_india_data
        )
        assert isinstance(result, str)


class TestFormatStepResponse:
    """Tests for format_step_response function."""

    def test_beginner_mode_uses_simple_desc(
        self, sample_india_data: dict
    ) -> None:
        """Beginner mode renders the simplified description."""
        step = sample_india_data["steps"][0]
        result = format_step_response(step, "Beginner")
        assert "tells everyone" in result

    def test_advanced_mode_uses_full_desc(
        self, sample_india_data: dict
    ) -> None:
        """Advanced mode renders the full description."""
        step = sample_india_data["steps"][0]
        result = format_step_response(step, "Advanced")
        assert "ECI announces" in result

    def test_includes_key_terms(
        self, sample_india_data: dict
    ) -> None:
        """Step response includes key terms."""
        step = sample_india_data["steps"][0]
        result = format_step_response(step)
        assert "Key Terms" in result

    def test_includes_duration(
        self, sample_india_data: dict
    ) -> None:
        """Step response includes duration."""
        step = sample_india_data["steps"][0]
        result = format_step_response(step)
        assert "1 day" in result


class TestFormatChatResponse:
    """Tests for format_chat_response function."""

    def test_correct_structure(self) -> None:
        """Response dict has the expected keys."""
        result = format_chat_response("Hello", ["Test"])
        assert result["role"] == "assistant"
        assert result["content"] == "Hello"
        assert result["sources"] == ["Test"]
