"""Input sanitization and validation for user-supplied data.

All user input must pass through these functions before processing
to guard against XSS, SQL injection, and path traversal attacks.
"""

import re
from config import MAX_INPUT_LENGTH, SUPPORTED_COUNTRIES
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Pre-compiled Patterns ---
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SQL_INJECTION_RE = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE"
    r"|EXEC|EXECUTE|TRUNCATE|MERGE)\b)",
    re.IGNORECASE,
)
_XSS_PATTERN_RE = re.compile(
    r"(<script|javascript:|on\w+\s*=)", re.IGNORECASE
)
_PATH_TRAVERSAL_RE = re.compile(r"\.\./|\.\.\\")


def sanitize_query(user_input: str) -> str:
    """Strip HTML tags, control characters, and enforce length limit.

    Args:
        user_input: The raw string from the user.

    Returns:
        A cleaned, length-limited string safe for downstream use.
    """
    # Strip HTML tags
    cleaned = _HTML_TAG_RE.sub("", user_input)
    # Remove control characters
    cleaned = _CONTROL_CHAR_RE.sub("", cleaned)
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    # Enforce max length
    cleaned = cleaned[:MAX_INPUT_LENGTH]
    return cleaned


def is_safe_input(user_input: str) -> bool:
    """Check the input for SQL injection, XSS, and path traversal.

    Args:
        user_input: The string to validate.

    Returns:
        True if the input passes all safety checks, False otherwise.
    """
    if _SQL_INJECTION_RE.search(user_input):
        logger.warning("SQL injection pattern detected: %s", user_input[:80])
        return False
    if _XSS_PATTERN_RE.search(user_input):
        logger.warning("XSS payload detected: %s", user_input[:80])
        return False
    if _PATH_TRAVERSAL_RE.search(user_input):
        logger.warning("Path traversal detected: %s", user_input[:80])
        return False
    return True


def validate_country(country: str) -> str:
    """Validate that the country string is in the supported list.

    Args:
        country: The country identifier to validate.

    Returns:
        The lowercased, validated country string.

    Raises:
        ValueError: If the country is not in SUPPORTED_COUNTRIES.
    """
    normalized = country.strip().lower()
    if normalized not in SUPPORTED_COUNTRIES:
        raise ValueError(
            f"Unsupported country: '{country}'. "
            f"Supported: {SUPPORTED_COUNTRIES}"
        )
    return normalized
