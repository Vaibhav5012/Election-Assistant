"""Tests for the google_services module.

Uses unittest.mock to avoid real Google API calls.
Covers Sheets logging, GA4 tracking, OAuth, and Drive export.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from utils.google_services import (
    GoogleSheetsLogger,
    export_session_to_drive,
    get_oauth_credentials,
    inject_ga4_script,
    track_event,
)


class TestGoogleSheetsLogger:
    """Tests for GoogleSheetsLogger class."""

    def test_log_query_appends_row(
        self, mock_sheets_service: MagicMock
    ) -> None:
        """log_query appends a row with correct data."""
        logger = GoogleSheetsLogger("fake.json", "sheet-id")
        logger._client = mock_sheets_service

        logger.log_query("India", "Ask Questions", "What is EVM?", "2026-01-01T00:00:00")

        ws = mock_sheets_service.open_by_key.return_value.worksheet.return_value
        ws.append_row.assert_called_once()
        row = ws.append_row.call_args[0][0]
        assert row[0] == "2026-01-01T00:00:00"
        assert row[1] == "India"

    def test_log_quiz_result(
        self, mock_sheets_service: MagicMock
    ) -> None:
        """log_quiz_result appends quiz score row."""
        logger = GoogleSheetsLogger("fake.json", "sheet-id")
        logger._client = mock_sheets_service

        logger.log_quiz_result("India", 8, 10)

        ws = mock_sheets_service.open_by_key.return_value.worksheet.return_value
        ws.append_row.assert_called_once()
        row = ws.append_row.call_args[0][0]
        assert row[1] == "India"
        assert row[2] == 8
        assert row[3] == 10

    def test_retry_on_failure(
        self, mock_sheets_service: MagicMock
    ) -> None:
        """Retries on transient failure then succeeds."""
        ws = mock_sheets_service.open_by_key.return_value.worksheet.return_value
        ws.append_row.side_effect = [Exception("timeout"), Exception("timeout"), None]

        logger = GoogleSheetsLogger("fake.json", "sheet-id")
        logger._client = mock_sheets_service

        # Should not raise — retries succeed on 3rd attempt
        logger.log_query("India", "Chat", "test", "2026-01-01")
        assert ws.append_row.call_count == 3

    def test_graceful_failure(
        self, mock_sheets_service: MagicMock
    ) -> None:
        """All retries fail but no exception propagates."""
        ws = mock_sheets_service.open_by_key.return_value.worksheet.return_value
        ws.append_row.side_effect = Exception("permanent failure")

        logger = GoogleSheetsLogger("fake.json", "sheet-id")
        logger._client = mock_sheets_service

        # Should NOT raise an exception
        logger.log_query("India", "Chat", "test", "2026-01-01")

    def test_disabled_returns_none(self) -> None:
        """get_sheets_logger returns None when disabled."""
        with patch("config.ENABLE_SHEETS", False):
            from utils.google_services import get_sheets_logger
            get_sheets_logger.clear()
            result = get_sheets_logger()
            assert result is None


class TestGA4Tracking:
    """Tests for GA4 script injection and event tracking."""

    def test_inject_script_contains_id(self) -> None:
        """GA4 script contains the measurement ID."""
        html = inject_ga4_script("G-TEST12345")
        assert "G-TEST12345" in html
        assert "<script" in html
        assert "gtag(" in html

    def test_track_event_output(self) -> None:
        """track_event returns valid JS with event name."""
        js = track_event("mode_selected", {"country": "india"})
        assert "mode_selected" in js
        assert "india" in js
        assert "gtag('event'" in js

    def test_track_event_empty_params(self) -> None:
        """track_event works with no params."""
        js = track_event("step_advanced")
        assert "step_advanced" in js
        assert "{}" in js


class TestOAuth:
    """Tests for OAuth2 integration."""

    def test_returns_none_when_disabled(self) -> None:
        """get_oauth_credentials returns None when auth disabled."""
        with patch("config.ENABLE_AUTH", False):
            result = get_oauth_credentials()
            assert result is None


class TestDriveExport:
    """Tests for Drive export functionality."""

    def test_requires_credentials(self) -> None:
        """Export returns None without credentials."""
        result = export_session_to_drive(
            credentials=None,
            chat_history=[],
            quiz_score=0,
            quiz_total=0,
        )
        assert result is None
