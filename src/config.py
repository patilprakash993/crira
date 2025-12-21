"""
Configuration and constants for CRIRA.
"""

from __future__ import annotations
from typing import Dict

import os, re

SAFE_MODE = os.getenv("CRIRA_SAFE_MODE", "true").lower() in ("1", "true", "yes")
USE_REAL_LLM = os.getenv("CRIRA_USE_REAL_LLM", "false").lower() in ("1", "true", "yes")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
LLM_MODEL = os.getenv("CRIRA_LLM_MODEL", "gemini-1.5-flash-latest")
CRITICAL_KEYWORDS = [
        'danger', 'dangerous', 'injury', 'urgent', 'immediate', 'recall',
        'stop using', 'explosion', 'fire', 'safety', 'hazard', 'not safe', 'serious', 'critical', 'asap', 'ruined'
    ]
ALLOWED_PII_PLACEHOLDERS = {
    "PII_EMAIL",
    "PII_PHONE",
    "PII_NAME",
    "PII_ADDRESS",
    "PII_ORDER",
}
# Response schema enforcement
ANALYSIS_OUTPUT_SCHEMA = {"sentiment", "key_issues_praise", "summary"}

PII_PATTERNS: Dict[str, re.Pattern] = {
    # simple but practical patterns
    "PII_EMAIL": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    # phone numbers: international-ish and domestic
    "PII_PHONE": re.compile(r"\+?\d[\d\-\s\(\)]{7,}\d"),
    # names (simple capitalized pair, avoids matching parts of addresses)
    "PII_NAME": re.compile(r"\b([A-Z][a-z]{1,}\s(?!Street\b|St\b|Road\b|Rd\b|Avenue\b|Ave\b|Boulevard\b|Blvd\b|Lane\b|Ln\b|Drive\b|Dr\b)[A-Z][a-z]{1,})\b"),
    # A more comprehensive, but still naive, address pattern that is not overly greedy.
    "PII_ADDRESS": re.compile(r"\b\d{1,5}\s(?:[A-Za-z0-9\s,]+\s(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)|[POBox\s\d]+)[,.\sA-Za-z0-9-]*?(?=\.\s[A-Z]|\Z)", flags=re.IGNORECASE),
    # order id pattern
    "PII_ORDER": re.compile(r"\b(?:ORDER|Order|order)[\-\s_]?\d{4,}\b"),
}
