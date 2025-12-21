"""Review analysis: PII redaction, analysis prompt, and structured parsing."""

from __future__ import annotations
import re

import json
import logging
import os
from typing import Any, Dict, Tuple
from prompts import ANALYSIS_FEW_SHOT, ANALYSIS_SYSTEM_PROMPT
from llm_client import call_llm
from utils import canonicalize_text, escape_brackets, redact_pii


logger = logging.getLogger(__name__)

def _parse_llm_json_output(raw_output: str) -> Dict[str, Any]:
    """
    Safely parse JSON from LLM output, with fallback for malformed responses.
    """
    try:
        # First, try to load the raw output directly
        return json.loads(raw_output)
    except json.JSONDecodeError:
        # If it fails, search for a JSON object within the string
        logger.warning("LLM output was not valid JSON, attempting to extract from text.")
        match = re.search(r"\{.*\}", raw_output, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                logger.error("Failed to parse extracted JSON from LLM output.")
        else:
            logger.error("No JSON object found in LLM output.")
    
    return {"sentiment": "neutral", "key_issues_praise": [], "summary": "Unable to parse LLM output."}

def analyze_review(raw_text: str) -> Dict[str, Any]:
    """
    Analyze a single review:
    - canonicalize and optionally escape bracket tokens
    - redact PII (if SAFE_MODE)
    - call LLM to extract sentiment, issues, summary (structured JSON)
    - validate and return a dict with keys: redacted_review, pii_found, sentiment, key_issues_praise, summary
    """
    # Re-evaluate SAFE_MODE inside the function to allow test-time patching.
    safe_mode = os.getenv("CRIRA_SAFE_MODE", "true").lower() in ("1", "true", "yes")

    text = canonicalize_text(raw_text)
    if safe_mode:
        redacted_text, pii_found = redact_pii(text)
        # escape brackets to prevent injection via bracket tokens
        redacted_text = escape_brackets(redacted_text)
    else:
        # unsafe mode: leave raw
        redacted_text = text
        pii_found = []

    # Build prompt
    prompt = f"{ANALYSIS_FEW_SHOT}\nReview: \"{redacted_text}\"\nOutput:"
    try:
        raw_output = call_llm(prompt=prompt, system=ANALYSIS_SYSTEM_PROMPT, max_tokens=400)
    except Exception as e:
        logger.exception("LLM call failed during analyze_review")
        # fallback safe structured response
        raw_output = json.dumps({"sentiment": "neutral", "key_issues_praise": [], "summary": "Analysis temporarily unavailable."})

    from config import ANALYSIS_OUTPUT_SCHEMA
    parsed = _parse_llm_json_output(raw_output)
    
    # Validate keys
    if not ANALYSIS_OUTPUT_SCHEMA.issubset(parsed.keys()):
        parsed_valid = {
            "sentiment": parsed.get("sentiment", "neutral"),
            "key_issues_praise": parsed.get("key_issues_praise", []),
            "summary": parsed.get("summary", ""),
        }
    else:
        parsed_valid = parsed

    return {
        "redacted_review": redacted_text,
        "pii_found": pii_found,
        "sentiment": parsed_valid["sentiment"],
        "key_issues_praise": parsed_valid["key_issues_praise"],
        "summary": parsed_valid["summary"],
    }
