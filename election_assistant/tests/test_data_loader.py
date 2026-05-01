"""Tests for the data_loader module.

Covers valid load, file not found, schema validation failure,
and malformed JSON scenarios.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.data_loader import (
    get_available_countries,
    load_election_data,
    validate_data,
)


class TestLoadElectionData:
    """Tests for load_election_data function."""

    def test_load_valid_data(
        self, tmp_path: Path, sample_india_data: dict
    ) -> None:
        """Loading a valid JSON file returns the expected data."""
        # Write sample data to a temp file
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "india.json").write_text(
            json.dumps(sample_india_data), encoding="utf-8"
        )

        # Copy schema to temp dir
        from config import SCHEMA_PATH

        schema_content = SCHEMA_PATH.read_text(encoding="utf-8")
        (data_dir / "schema.json").write_text(
            schema_content, encoding="utf-8"
        )

        with patch("utils.data_loader.DATA_DIR", data_dir), patch(
            "utils.data_loader.SCHEMA_PATH", data_dir / "schema.json"
        ):
            # Clear cache for this test
            load_election_data.clear()
            result = load_election_data("india")

        assert result["country"] == "India"
        assert len(result["steps"]) >= 1

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Loading a non-existent country raises FileNotFoundError."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        with patch("utils.data_loader.DATA_DIR", data_dir):
            load_election_data.clear()
            with pytest.raises(FileNotFoundError):
                load_election_data("atlantis")

    def test_malformed_json(
        self, tmp_path: Path, malformed_json_path: Path
    ) -> None:
        """Loading a malformed JSON file raises an error."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        # Copy malformed file as a country file
        import shutil

        shutil.copy(malformed_json_path, data_dir / "bad.json")

        with patch("utils.data_loader.DATA_DIR", data_dir):
            load_election_data.clear()
            with pytest.raises(Exception):
                load_election_data("bad")


class TestValidateData:
    """Tests for validate_data function."""

    def test_valid_data_passes(
        self, sample_india_data: dict
    ) -> None:
        """Valid data passes schema validation."""
        assert validate_data(sample_india_data) is True

    def test_missing_required_fields(
        self, invalid_json_data: dict
    ) -> None:
        """Data missing required fields fails validation."""
        import jsonschema

        with pytest.raises(jsonschema.ValidationError):
            validate_data(invalid_json_data)

    def test_empty_steps_array(
        self, sample_india_data: dict
    ) -> None:
        """Data with an empty steps array fails validation."""
        import jsonschema

        sample_india_data["steps"] = []
        with pytest.raises(jsonschema.ValidationError):
            validate_data(sample_india_data)


class TestGetAvailableCountries:
    """Tests for get_available_countries function."""

    def test_returns_sorted_countries(
        self, tmp_path: Path, sample_india_data: dict
    ) -> None:
        """Returns sorted list of country names from data dir."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "india.json").write_text("{}")
        (data_dir / "usa.json").write_text("{}")
        (data_dir / "schema.json").write_text("{}")

        with patch("utils.data_loader.DATA_DIR", data_dir):
            countries = get_available_countries()

        assert countries == ["india", "usa"]
        assert "schema" not in countries
