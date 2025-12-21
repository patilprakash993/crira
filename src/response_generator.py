"""Generates customer-facing responses with CRITICAL_REF handling and injection defenses."""

from __future__ import annotations
import re

import logging
from typing import Any, Dict

from prompts import RESPONSE_SYSTEM_PROMPT
from llm_client import call_llm
from utils import contains_critical_keyword, generate_critical_ref, canonicalize_text, escape_brackets
from config import SAFE_MODE, CRITICAL_KEYWORDS

logger = logging.getLogger(__name__)


def generate_response(analyzed: Dict[str, Any], raw_review_text: str) -> Dict[str, Any]:
    """
    Generates an on-brand response.
    - analyzed: result from analyze_review
    - raw_review_text: original review text
    Returns:
      {
        "response_text": "...",
        "is_critical": bool,
        "critical_ref": Optional[str]
      }
    Business rules:
      - If critical keyword present, backend appends CRITICAL_REF (UUID) AFTER LLM output.
      - In SAFE_MODE, we forcibly escape bracket tokens before sending to LLM and forbid LLM to create CRITICAL_REF strings.
      - Validate final output to ensure no CRITICAL_REF appears in LLM output.
    """
    # canonicalize
    canonical_review = canonicalize_text(raw_review_text)

    is_critical = contains_critical_keyword(canonical_review, CRITICAL_KEYWORDS)

    # Prepare prompt input for LLM
    # Provide the LLM with the sanitized/redacted review (not raw)
    review_for_llm = analyzed["redacted_review"]
    if SAFE_MODE:
        review_for_llm = escape_brackets(review_for_llm)

    prompt = (
        f"Customer review: \"{review_for_llm}\"\n\n"
        f"Sentiment: {analyzed.get('sentiment')}\n"
        f"Issues/Praise: {analyzed.get('key_issues_praise')}\n"
        f"Summary: {analyzed.get('summary')}\n\n"
        "Please write an empathetic, professional response to the customer following the system instructions."
    )

    llm_output = call_llm(prompt=prompt, system=RESPONSE_SYSTEM_PROMPT, max_tokens=400)

    # Defensive check: ensure LLM did NOT produce CRITICAL_REF-like token
    if "[CRITICAL_REF:" in llm_output:
        logger.warning("LLM returned CRITICAL_REF-like token. Stripping it.")
        # Remove any bracketed CRITICAL_REFs in LLM output
        llm_output = re.sub(r"\[CRITICAL_REF:[^\]]*\]", "", llm_output)

    # In SAFE mode we also ensure no PII placeholders leaked
    for p in ("[PII_EMAIL]", "[PII_PHONE]", "[PII_NAME]", "[PII_ADDRESS]", "[PII_ORDER]"):
        if p in llm_output:
            logger.warning("LLM output contained PII placeholder; replacing with generic mention.")
            llm_output = llm_output.replace(p, "[REDACTED_PII]")

    # The backend is always responsible for appending the critical reference.
    # This prevents the LLM from creating or manipulating it.
    critical_ref = None
    final_response = llm_output.strip()
    if is_critical:
        critical_ref = generate_critical_ref()
        final_response = f"{final_response}\n\n{critical_ref}"

    return {"response_text": final_response, "is_critical": is_critical, "critical_ref": critical_ref}
