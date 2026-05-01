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

    def test_returns_none_when_credentials_absent(self) -> None:
        """get_oauth_credentials returns None when client secret is missing."""
        with patch("config.ENABLE_AUTH", True), patch("config.GOOGLE_CLIENT_SECRET_PATH", ""):
            result = get_oauth_credentials()
            assert result is None

    @patch("googleapiclient.discovery.build")
    def test_get_user_info(self, mock_build: MagicMock) -> None:
        """get_user_info returns profile data with mock credentials."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_user = {"name": "Test User", "email": "test@example.com"}
        mock_service.userinfo.return_value.get.return_value.execute.return_value = mock_user
        
        mock_creds = MagicMock()
        from utils.google_services import get_user_info
        result = get_user_info(mock_creds)
        assert result == mock_user

    def test_get_user_info_no_creds(self) -> None:
        """get_user_info returns None if no credentials."""
        from utils.google_services import get_user_info
        result = get_user_info(None)
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

    @patch("googleapiclient.discovery.build")
    def test_export_success_with_mock_credentials(self, mock_build: MagicMock) -> None:
        """Export succeeds with mock credentials and returns a valid URL."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_doc = {"documentId": "12345_TEST_ID"}
        mock_service.documents.return_value.create.return_value.execute.return_value = mock_doc

        mock_creds = MagicMock()
        result = export_session_to_drive(
            credentials=mock_creds,
            chat_history=[{"role": "user", "content": "hello"}],
            quiz_score=5,
            quiz_total=10,
        )
        assert result == "https://docs.google.com/document/d/12345_TEST_ID/edit"

        # Verify batchUpdate was called to insert body content
        batch_call = mock_service.documents.return_value.batchUpdate
        batch_call.assert_called_once()
        call_kwargs = batch_call.call_args
        body = call_kwargs[1]["body"] if "body" in call_kwargs[1] else call_kwargs[0][0]
        requests = body["requests"]
        assert len(requests) == 1
        insert = requests[0]["insertText"]
        assert insert["location"]["index"] == 1
        assert "hello" in insert["text"]
        assert "Score: 5/10" in insert["text"]

    @patch("googleapiclient.discovery.build")
    def test_export_empty_session(self, mock_build: MagicMock) -> None:
        """Export with no chat and no quiz creates doc but skips batchUpdate."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_doc = {"documentId": "EMPTY_DOC_ID"}
        mock_service.documents.return_value.create.return_value.execute.return_value = mock_doc

        mock_creds = MagicMock()
        result = export_session_to_drive(
            credentials=mock_creds,
            chat_history=[],
            quiz_score=0,
            quiz_total=0,
        )
        assert result == "https://docs.google.com/document/d/EMPTY_DOC_ID/edit"

        # batchUpdate should NOT be called when content is empty
        batch_call = mock_service.documents.return_value.batchUpdate
        batch_call.assert_not_called()

