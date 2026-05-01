"""Tests for the validators module.

Covers sanitization, safety checks, and country validation
including SQL injection, XSS, path traversal, and normal inputs.
"""

from __future__ import annotations

import pytest

from utils.validators import (
    is_safe_input,
    sanitize_query,
    validate_country,
)


class TestSanitizeQuery:
    """Tests for the sanitize_query function."""

    def test_strips_html_tags(self) -> None:
        """HTML tags are removed from input."""
        result = sanitize_query("<b>bold</b> text")
        assert "<b>" not in result
        assert "bold" in result

    def test_removes_control_characters(self) -> None:
        """Control characters are stripped."""
        result = sanitize_query("hello\x00world\x0b")
        assert "\x00" not in result
        assert "\x0b" not in result
        assert "helloworld" in result

    def test_enforces_max_length(self) -> None:
        """Input exceeding max length is truncated to 500 chars."""
        long_input = "a" * 600
        result = sanitize_query(long_input)
        assert len(result) == 500

    def test_strips_whitespace(self) -> None:
        """Leading and trailing whitespace is removed."""
        result = sanitize_query("  hello  ")
        assert result == "hello"

    def test_normal_input_unchanged(self) -> None:
        """Clean input passes through unchanged."""
        result = sanitize_query("What is EVM?")
        assert result == "What is EVM?"


class TestIsSafeInput:
    """Tests for the is_safe_input function."""

    def test_sql_injection_detected(self) -> None:
        """SQL injection patterns are rejected."""
        assert is_safe_input("SELECT * FROM users") is False
        assert is_safe_input("DROP TABLE data") is False
        assert is_safe_input("1; DELETE FROM votes") is False

    def test_xss_payload_detected(self) -> None:
        """XSS payloads are rejected."""
        assert is_safe_input("<script>alert('xss')</script>") is False
        assert is_safe_input("javascript:alert(1)") is False
        assert is_safe_input('onload=alert("x")') is False

    def test_path_traversal_detected(self) -> None:
        """Path traversal sequences are rejected."""
        assert is_safe_input("../../etc/passwd") is False
        assert is_safe_input("..\\windows\\system32") is False

    def test_normal_input_accepted(self) -> None:
        """Clean input passes all safety checks."""
        assert is_safe_input("What is the EVM?") is True
        assert is_safe_input("Tell me about elections") is True

    def test_empty_string_accepted(self) -> None:
        """Empty string is considered safe."""
        assert is_safe_input("") is True


class TestValidateCountry:
    """Tests for the validate_country function."""

    def test_valid_country(self) -> None:
        """Valid country names are accepted and lowercased."""
        assert validate_country("India") == "india"
        assert validate_country("USA") == "usa"

    def test_invalid_country_raises(self) -> None:
        """Invalid country names raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported country"):
            validate_country("atlantis")

    def test_whitespace_handling(self) -> None:
        """Country names with whitespace are trimmed."""
        assert validate_country("  india  ") == "india"
