"""Utility helpers."""
from __future__ import annotations

import re
import uuid
from typing import Tuple, List

from config import PII_PATTERNS
def canonicalize_text(text: str) -> str:
    """
    Canonicalize input text to reduce injection risks using an allow-list approach.
    - Keep only a predefined set of safe characters (alphanumeric, common punctuation).
    - Collapse excessive whitespace

    Args:
        text: The input string to canonicalize.

    Returns:
        The canonicalized string with only allowed characters and normalized
        whitespace.
    """
    # Allow-list of characters: alphanumeric, space, and common punctuation.
    # The regex pattern matches any character NOT in this set.
    allowed_chars_pattern = r"[^a-zA-Z0-9\s.,!?'\"()&%$#@_-]"
    # Remove any character not on the allow-list
    text = re.sub(allowed_chars_pattern, "", text)
    # Collapse all whitespace to single spaces and strip leading/trailing space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate_critical_ref() -> str:
    """
    Generates a secure CRITICAL_REF string containing a UUID4.
    This is done in backend code to prevent LLM from injecting content into the ref.

    Returns:
        A string in the format '[CRITICAL_REF: <UUID>]'.
    """
    u = uuid.uuid4()
    return f"[CRITICAL_REF: {u}]"


def contains_critical_keyword(text: str, keywords: list[str]) -> bool:
    """
    Check if the text contains any of the specified critical keywords (case-insensitive).

    Args:
        text: The input string to check.
        keywords: A list of keywords to search for.

    Returns:
        True if any keyword is found, False otherwise.
    """
    lowered = text.lower()
    return any(k.lower() in lowered for k in keywords)


def escape_brackets(text: str) -> str:
    """
    Escape square brackets to limit attempts to inject bracketed tokens.
    In safe mode we will escape them before giving to LLM.

    Args:
        text: The input string.

    Returns:
        The string with square brackets escaped.
    """
    return text.replace("[", "\\[").replace("]", "\\]")


def redact_pii(text: str) -> Tuple[str, List[str]]:
    """
    Replace recognized PII with placeholders and return the redacted text and list of placeholders found.
    Deterministic regex-based redaction is used to avoid exposing raw PII to the LLM.

    Args:
        text: The input string to redact.

    Returns:
        A tuple containing:
        - The redacted string with PII replaced by placeholders.
        - A list of the PII types found (e.g., ['PII_EMAIL']).
    """
    found: List[str] = []
    redacted = text
    for tag, pattern in PII_PATTERNS.items():
        # find occurrences
        if pattern.search(redacted):
            found.append(tag)
            # replace all matches with placeholder
            redacted = pattern.sub(f"[{tag}]", redacted)
    return redacted, found
