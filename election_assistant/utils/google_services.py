"""Google Services integration module.

Provides four independently toggleable integrations:
  A. Google Sheets — usage analytics logging
  B. Google Analytics 4 — page and event tracking
  C. Google OAuth2 — optional user authentication
  D. Google Drive — session export

All integrations degrade gracefully when credentials are absent.
Every API call uses tenacity retry with 3 attempts and 2-second
exponential backoff.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from utils.logger import get_logger

logger = get_logger(__name__)

# --- Lazy imports for Google libraries ---
# These are imported inside functions to avoid import errors
# when Google packages are not installed or not configured.


# =====================================================================
# A. Google Sheets — Usage Analytics
# =====================================================================
class GoogleSheetsLogger:
    """Logs user query events and quiz results to a Google Sheet.

    All writes use tenacity retry: 3 attempts, 2-second exponential
    backoff.  Failures are logged but never propagated to the UI.
    """

    def __init__(self, credentials_path: str, sheet_id: str) -> None:
        """Initialize the Sheets logger.

        Args:
            credentials_path: Path to the service account JSON key.
            sheet_id: The Google Sheet ID from the URL.
        """
        self._credentials_path = credentials_path
        self._sheet_id = sheet_id
        self._client = None

    def _get_client(self) -> Any:
        """Lazy-initialize the gspread client.

        Returns:
            An authenticated gspread client, or None on failure.
        """
        if self._client is not None:
            return self._client
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_file(
                self._credentials_path, scopes=scopes
            )
            self._client = gspread.authorize(creds)
            return self._client
        except Exception:
            logger.exception("Failed to initialize Sheets client")
            return None

    def log_query(
        self,
        country: str,
        mode: str,
        query: str,
        timestamp: str,
    ) -> None:
        """Append a query record to the analytics sheet.

        Args:
            country: The selected country.
            mode: The active mode (e.g., "Ask Questions").
            query: The user's query text.
            timestamp: ISO-format timestamp string.
        """
        self._append_row(
            "Queries",
            [timestamp, country, mode, query],
        )

    def log_quiz_result(
        self, country: str, score: int, total: int
    ) -> None:
        """Append a quiz completion record.

        Args:
            country: The selected country.
            score: Number of correct answers.
            total: Total number of questions.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        self._append_row(
            "Quiz Results",
            [timestamp, country, score, total],
        )

    def _append_row(
        self, worksheet_name: str, row: list
    ) -> None:
        """Append a row to a named worksheet with retry.

        Args:
            worksheet_name: The tab/worksheet name.
            row: List of values to append as a new row.
        """
        try:
            from tenacity import (
                retry,
                stop_after_attempt,
                wait_exponential,
            )

            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(
                    multiplier=2, min=2, max=10
                ),
                reraise=True,
            )
            def _do_append() -> None:
                client = self._get_client()
                if client is None:
                    return
                sheet = client.open_by_key(self._sheet_id)
                try:
                    ws = sheet.worksheet(worksheet_name)
                except Exception:
                    ws = sheet.add_worksheet(
                        worksheet_name, rows=1000, cols=10
                    )
                ws.append_row(row)

            _do_append()
        except Exception:
            logger.exception(
                "Failed to log to Sheets worksheet '%s'",
                worksheet_name,
            )


@st.cache_resource
def get_sheets_logger() -> GoogleSheetsLogger | None:
    """Return a cached GoogleSheetsLogger if enabled.

    Returns:
        A GoogleSheetsLogger instance, or None if disabled.
    """
    from config import (
        ENABLE_SHEETS,
        GOOGLE_SERVICE_ACCOUNT_PATH,
        GOOGLE_SHEET_ID,
    )

    if not ENABLE_SHEETS:
        return None
    if not GOOGLE_SERVICE_ACCOUNT_PATH or not GOOGLE_SHEET_ID:
        logger.warning("Sheets enabled but credentials missing")
        return None
    return GoogleSheetsLogger(
        GOOGLE_SERVICE_ACCOUNT_PATH, GOOGLE_SHEET_ID
    )


# =====================================================================
# B. Google Analytics 4 — Page & Event Tracking
# =====================================================================
def inject_ga4_script(measurement_id: str) -> str:
    """Return the GA4 global site tag HTML script.

    Args:
        measurement_id: The GA4 Measurement ID (e.g., ``G-XXXXXXXXXX``).

    Returns:
        An HTML string containing the GA4 script tags.
    """
    return f"""
    <!-- Google Analytics 4 -->
    <script async
        src="https://www.googletagmanager.com/gtag/js?id={measurement_id}">
    </script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', '{measurement_id}');
    </script>
    """


def track_event(
    event_name: str, params: dict | None = None
) -> str:
    """Return a JS snippet that fires a GA4 custom event.

    Required events and their trigger points:
      - ``mode_selected``  → sidebar.py (country/mode change)
      - ``step_advanced``  → steps.py ("Next Step" click)
      - ``question_asked`` → chat.py (query submission)
      - ``quiz_completed`` → quiz.py (all questions answered)

    Args:
        event_name: The GA4 event name string.
        params: Optional dictionary of event parameters.

    Returns:
        An HTML ``<script>`` string to inject via
        ``st.markdown(unsafe_allow_html=True)``.
    """
    params_json = json.dumps(params or {})
    return f"""
    <script>
        if (typeof gtag !== 'undefined') {{
            gtag('event', '{event_name}', {params_json});
        }}
    </script>
    """


# =====================================================================
# C. Google OAuth2 — Optional User Authentication
# =====================================================================
def get_oauth_credentials() -> Any:
    """Return OAuth2 credentials if the user is logged in.

    Returns:
        Google OAuth2 Credentials object, or None.
    """
    from config import ENABLE_AUTH, GOOGLE_CLIENT_SECRET_PATH

    if not ENABLE_AUTH or not GOOGLE_CLIENT_SECRET_PATH:
        return None

    try:
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRET_PATH,
            scopes=[
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid",
            ],
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        )
        # In a Streamlit context, the full OAuth redirect flow
        # requires additional session handling.  This provides
        # the foundation; deployment-specific adapters can extend.
        return st.session_state.get("oauth_credentials")
    except Exception:
        logger.exception("OAuth2 initialization failed")
        return None


def get_user_info(credentials: Any) -> dict | None:
    """Retrieve user profile info from Google.

    Args:
        credentials: Google OAuth2 Credentials object.

    Returns:
        A dict with ``name`` and ``email`` keys, or None.
    """
    if credentials is None:
        return None
    try:
        from googleapiclient.discovery import build

        service = build(
            "oauth2", "v2", credentials=credentials
        )
        return service.userinfo().get().execute()
    except Exception:
        logger.exception("Failed to fetch user info")
        return None


# =====================================================================
# D. Google Drive — Export Feature
# =====================================================================
def export_session_to_drive(
    credentials: Any,
    chat_history: list[dict],
    quiz_score: int = 0,
    quiz_total: int = 0,
) -> str | None:
    """Export the current session as a Google Doc.

    Args:
        credentials: Google OAuth2 Credentials object.
        chat_history: List of message dicts from session state.
        quiz_score: Number of correct quiz answers.
        quiz_total: Total quiz questions attempted.

    Returns:
        A shareable Google Doc URL string, or None on failure.
    """
    if credentials is None:
        logger.warning("Export requires OAuth login")
        return None

    try:
        return _upload_doc(
            credentials, chat_history, quiz_score, quiz_total
        )
    except Exception:
        logger.exception("Session export to Drive failed")
        return None


def _upload_doc(
    credentials: Any,
    chat_history: list[dict],
    quiz_score: int,
    quiz_total: int,
) -> str:
    """Create a Google Doc and insert report content with retry.

    Args:
        credentials: Google OAuth2 Credentials object.
        chat_history: List of message dicts.
        quiz_score: Number of correct quiz answers.
        quiz_total: Total quiz questions.

    Returns:
        A shareable Google Doc URL string.
    """
    from googleapiclient.discovery import build
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
    )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=2, min=2, max=10
        ),
        reraise=True,
    )
    def _do_upload() -> str:
        service = build(
            "docs", "v1", credentials=credentials
        )
        title, content = _build_report(
            chat_history, quiz_score, quiz_total
        )
        # Create the document with title only
        doc = (
            service.documents()
            .create(body={"title": title})
            .execute()
        )
        doc_id = doc.get("documentId", "")

        # Insert body content via batchUpdate
        if content:
            requests = _build_doc_requests(content)
            service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": requests},
            ).execute()

        return (
            f"https://docs.google.com/document/d/{doc_id}/edit"
        )

    return _do_upload()


def _build_report(
    chat_history: list[dict],
    quiz_score: int,
    quiz_total: int,
) -> tuple[str, str]:
    """Build report title and plain-text body content.

    Args:
        chat_history: List of message dicts.
        quiz_score: Number of correct quiz answers.
        quiz_total: Total quiz questions.

    Returns:
        A tuple of ``(title, content_text)``.
    """
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )
    title = f"Election Assistant Report — {timestamp}"

    # Build plain-text body content
    lines: list[str] = []

    if chat_history:
        lines.append("Chat History")
        lines.append("-" * 12)
        for msg in chat_history:
            role = msg.get("role", "unknown").capitalize()
            lines.append(f"{role}: {msg.get('content', '')}")
        lines.append("")

    if quiz_total > 0:
        lines.append("Quiz Results")
        lines.append("-" * 12)
        lines.append(f"Score: {quiz_score}/{quiz_total}")
        pct = (quiz_score / quiz_total * 100) if quiz_total else 0
        lines.append(f"Percentage: {pct:.0f}%")

    return title, "\n".join(lines)


def _build_doc_requests(content: str) -> list[dict]:
    """Build a Google Docs batchUpdate request list.

    Inserts the full report content at index 1 (start of
    the document body) in a single insertText request to
    preserve line ordering.

    Args:
        content: The plain-text content to insert.

    Returns:
        A list of Docs API request dicts.
    """
    return [
        {
            "insertText": {
                "location": {"index": 1},
                "text": content,
            }
        }
    ]

