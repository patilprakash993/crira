"""
Configuration loader for CRIRA.

This module loads configuration from config.json and allows environment
variables to override the values. This provides a flexible configuration
system where defaults can be stored in the JSON file and secrets or
environment-specific settings can be provided via environment variables.
"""
from __future__ import annotations
import os, re
from typing import Any, Dict, List, Set

import json
from pathlib import Path

def _load_config():
    """Loads configuration from JSON file."""
    config_path = Path(__file__).parent / 'config.json'
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
_config = _load_config()

def _get_env_var(var_name: str, default: Any) -> Any:
    """Gets an environment variable, casting boolean-like strings."""
    value = os.getenv(var_name)
    if value is None:
        return default
    if isinstance(default, bool):
        return value.lower() in ("1", "true", "yes")
    return value

# --- Configuration Values ---
# Load from config.json and allow environment variables to override.
SAFE_MODE: bool = _get_env_var("CRIRA_SAFE_MODE", _config.get("SAFE_MODE", True))
USE_REAL_LLM: bool = _get_env_var("CRIRA_USE_REAL_LLM", _config.get("USE_REAL_LLM", False))
GOOGLE_API_KEY: str = _get_env_var("GOOGLE_API_KEY", _config.get("GOOGLE_API_KEY", ""))
LLM_MODEL: str = _get_env_var("CRIRA_LLM_MODEL", _config.get("LLM_MODEL", "gemini-1.5-flash-latest"))
CRITICAL_KEYWORDS: List[str] = _config.get("CRITICAL_KEYWORDS", [])
ALLOWED_PII_PLACEHOLDERS: Set[str] = set(_config.get("ALLOWED_PII_PLACEHOLDERS", []))
ANALYSIS_OUTPUT_SCHEMA: Set[str] = set(_config.get("ANALYSIS_OUTPUT_SCHEMA", []))

def _compile_pii_patterns() -> Dict[str, re.Pattern]:
    """Loads and compiles PII regex patterns from config."""
    patterns = {}
    for key, pattern_str in _config.get("PII_PATTERNS", {}).items():
        # The 'PII_ADDRESS' pattern uses case-insensitivity
        flags = re.IGNORECASE if key == "PII_ADDRESS" else 0
        patterns[key] = re.compile(pattern_str, flags)
    return patterns
PII_PATTERNS: Dict[str, re.Pattern] = _compile_pii_patterns()

DUMMY_LLM_KEYWORDS: Dict[str, Any] = _config.get("DUMMY_LLM_KEYWORDS", {})
