"""Shared pytest fixtures for the Election Assistant test suite.

Provides mock data, mock session state, and Google API mocks
to avoid real I/O in unit tests.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def sample_india_data() -> dict:
    """Return a minimal valid India election data dictionary."""
    return {
        "country": "India",
        "election_type": "General Election (Lok Sabha)",
        "steps": [
            {
                "id": 1,
                "title": "Announcement of Elections",
                "description": "The ECI announces the schedule.",
                "description_beginner": "The ECI tells everyone when the election happens.",
                "duration": "1 day",
                "responsible_party": "Election Commission of India",
                "key_terms": ["Model Code of Conduct"],
                "did_you_know": "India has over 900 million eligible voters.",
            },
            {
                "id": 2,
                "title": "Nomination of Candidates",
                "description": "Candidates file nomination papers.",
                "description_beginner": "People who want to run fill out forms.",
                "duration": "7-10 days",
                "responsible_party": "Returning Officers",
                "key_terms": ["Nomination Paper"],
                "did_you_know": "Over 8,000 candidates filed in 2024.",
            },
        ],
        "timeline": {
            "phases": [
                {
                    "id": 1,
                    "name": "Pre-Election Phase",
                    "start_offset_days": -90,
                    "end_offset_days": -30,
                    "color": "#1565C0",
                    "description": "Voter registration and preparation.",
                },
                {
                    "id": 2,
                    "name": "Campaign Phase",
                    "start_offset_days": -30,
                    "end_offset_days": -2,
                    "color": "#F57C00",
                    "description": "Active campaigning by parties.",
                },
            ],
        },
        "roles": [
            {
                "name": "Election Commission of India",
                "abbreviation": "ECI",
                "description": "The constitutional body for elections.",
                "powers": ["Announce schedule", "Enforce MCC"],
            },
        ],
        "key_terms": [
            {
                "term": "EVM",
                "full_form": "Electronic Voting Machine",
                "definition": "Device used to record votes.",
                "introduced": 1982,
            },
        ],
        "quiz": [
            {
                "id": 1,
                "question": "Which body conducts elections in India?",
                "options": [
                    "Supreme Court",
                    "Election Commission of India",
                    "Parliament",
                    "President's Office",
                ],
                "correct_index": 1,
                "explanation": "The ECI is the constitutional authority.",
            },
        ],
    }


@pytest.fixture
def sample_usa_data() -> dict:
    """Return a minimal valid USA election data dictionary."""
    return {
        "country": "USA",
        "election_type": "Presidential Election",
        "steps": [
            {
                "id": 1,
                "title": "Primary Elections",
                "description": "States hold primaries or caucuses.",
                "description_beginner": "States vote to pick party candidates.",
                "duration": "February - June",
                "responsible_party": "State Governments",
                "key_terms": ["Primary", "Caucus"],
                "did_you_know": "Iowa traditionally holds the first caucus.",
            },
        ],
        "timeline": {
            "phases": [
                {
                    "id": 1,
                    "name": "Primary Season",
                    "start_offset_days": -300,
                    "end_offset_days": -150,
                    "color": "#1565C0",
                    "description": "State primaries and caucuses.",
                },
            ],
        },
        "roles": [
            {
                "name": "Federal Election Commission",
                "abbreviation": "FEC",
                "description": "Enforces campaign finance laws.",
                "powers": ["Enforce limits", "Require disclosures"],
            },
        ],
        "key_terms": [
            {
                "term": "Electoral College",
                "full_form": "United States Electoral College",
                "definition": "Body of 538 electors.",
                "introduced": 1787,
            },
        ],
        "quiz": [
            {
                "id": 1,
                "question": "How many electoral votes to win?",
                "options": ["218", "270", "326", "435"],
                "correct_index": 1,
                "explanation": "270 out of 538 electoral votes needed.",
            },
        ],
    }


@pytest.fixture
def invalid_json_data() -> dict:
    """Return a data dict that fails schema validation."""
    return {
        "country": "Invalid",
        # Missing required fields: election_type, steps, etc.
    }


@pytest.fixture
def malformed_json_path(tmp_path: Path) -> Path:
    """Create a temporary file with malformed JSON content.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to the malformed JSON file.
    """
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{this is not valid json", encoding="utf-8")
    return bad_file


@pytest.fixture
def valid_json_path(tmp_path: Path, sample_india_data: dict) -> Path:
    """Create a temporary valid JSON data file.

    Args:
        tmp_path: Pytest's temporary directory fixture.
        sample_india_data: The sample India data fixture.

    Returns:
        Path to the valid JSON file.
    """
    file_path = tmp_path / "india.json"
    file_path.write_text(
        json.dumps(sample_india_data), encoding="utf-8"
    )
    return file_path


@pytest.fixture
def mock_session_state() -> dict:
    """Return a mock session state dictionary."""
    return {
        "messages": [],
        "current_step": 0,
        "quiz_score": 0,
        "quiz_index": 0,
        "quiz_answers": [],
        "quiz_shuffled_options": {},
        "steps_completed": set(),
        "theme": "light",
        "reading_level": "Beginner",
        "country": "india",
        "mode": "Learn Step-by-Step",
    }


@pytest.fixture
def mock_google_credentials() -> MagicMock:
    """Return a mock Google OAuth2 credentials object."""
    creds = MagicMock()
    creds.valid = True
    creds.token = "mock-token-12345"
    return creds


@pytest.fixture
def mock_sheets_service() -> MagicMock:
    """Return a mock gspread client."""
    client = MagicMock()
    sheet = MagicMock()
    worksheet = MagicMock()
    client.open_by_key.return_value = sheet
    sheet.worksheet.return_value = worksheet
    return client
