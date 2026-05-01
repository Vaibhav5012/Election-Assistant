"""Load and validate election data from JSON files.

Provides cached data-loading functions to avoid redundant file I/O
on Streamlit rerenders.
"""

import json
from pathlib import Path

import jsonschema
import streamlit as st

from config import CACHE_TTL, DATA_DIR, SCHEMA_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


@st.cache_data(ttl=CACHE_TTL)
def load_election_data(country: str) -> dict:
    """Load and validate election data for a given country.

    Args:
        country: ISO country name string (e.g., ``"india"``).

    Returns:
        Validated dictionary containing election steps, timeline,
        roles, and terms.

    Raises:
        FileNotFoundError: If the country JSON file does not exist.
        jsonschema.ValidationError: If the JSON fails schema validation.
    """
    file_path = DATA_DIR / f"{country.lower()}.json"
    if not file_path.exists():
        logger.error("Data file not found: %s", file_path)
        raise FileNotFoundError(f"No data file for country: {country}")

    with open(file_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Validate against schema
    validate_data(data)
    logger.info("Loaded and validated data for: %s", country)
    return data


def validate_data(data: dict) -> bool:
    """Validate election data against the JSON schema.

    Args:
        data: The parsed JSON dictionary to validate.

    Returns:
        True if validation passes.

    Raises:
        jsonschema.ValidationError: If validation fails.
        FileNotFoundError: If the schema file is missing.
    """
    if not SCHEMA_PATH.exists():
        logger.error("Schema file not found: %s", SCHEMA_PATH)
        raise FileNotFoundError(f"Schema file missing: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
        schema = json.load(fh)

    jsonschema.validate(instance=data, schema=schema)
    return True


@st.cache_data(ttl=CACHE_TTL)
def get_available_countries() -> list[str]:
    """Scan the data directory for available country JSON files.

    Returns:
        A sorted list of country name strings (file stems),
        excluding the schema file.
    """
    json_files = DATA_DIR.glob("*.json")
    countries = [
        f.stem
        for f in json_files
        if f.stem != "schema"
    ]
    return sorted(countries)
