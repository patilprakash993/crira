"""LLM client wrapper with a dummy fallback for tests."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional
import logging

from config import GOOGLE_API_KEY, USE_REAL_LLM, LLM_MODEL, DUMMY_LLM_KEYWORDS
from utils import escape_brackets

logger = logging.getLogger(__name__)


def call_llm(prompt: str, system: str = "", max_tokens: int = 400) -> str:
    """
    Calls the configured LLM. If USE_REAL_LLM is False, uses a deterministic dummy.
    The function returns the raw text response from the LLM.
    """
    if USE_REAL_LLM:
        try:
            # JIT (Just-In-Time) import and configuration
            import google.generativeai as genai

            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is not set, but USE_REAL_LLM is true.")

            genai.configure(api_key=GOOGLE_API_KEY)

            model = genai.GenerativeModel(
                LLM_MODEL,
                system_instruction=system,
                # We handle safety via input sanitization; prevent Gemini from blocking valid reviews.
                safety_settings={'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE', 'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'}
            )
            response = model.generate_content(prompt, generation_config={"max_output_tokens": max_tokens, "temperature": 0.7})
            return response.text
        except ImportError:
            logger.error("google-generativeai is not installed. Please run 'pip install google-generativeai'")
        except ValueError as e:
            logger.error(e)
        except Exception as e:
            logger.exception("Error calling the Gemini API. Falling back to dummy response.")

    # Dummy deterministic behaviour for testing and offline runs
    return dummy_llm_response(prompt, system)


def dummy_llm_response(prompt: str, system: str) -> str:
    """
    A deterministic placeholder that simulates LLM behavior, including common failure modes for testing.
    It can be triggered to produce specific errors by including special strings in the prompt.
    """
    # --- Error Simulation Triggers for Testing ---
    # These allow tests to verify the application's error handling.
    if "__DUMMY_ERROR_MALFORMED_JSON__" in prompt:
        logger.info("Dummy LLM: Simulating malformed JSON.")
        return '{"sentiment": "negative", "key_issues_praise": ["broken item"], "summary": "Item arrived broken."' # Intentionally malformed
    if "__DUMMY_ERROR_INCOMPLETE_JSON__" in prompt:
        logger.info("Dummy LLM: Simulating incomplete JSON.")
        return '{"sentiment": "negative", "summary": "Customer is unhappy."}' # Missing 'key_issues_praise'
    if "__DUMMY_ERROR_HALLUCINATE_REF__" in prompt:
        logger.info("Dummy LLM: Simulating hallucinated CRITICAL_REF.")
        return "We are very sorry for the issue. [CRITICAL_REF: dummy-hallucination-abc-123]"
    if "__DUMMY_ERROR_HALLUCINATE_PII__" in prompt:
        logger.info("Dummy LLM: Simulating hallucinated PII placeholder.")
        return "Thank you for your feedback. We will follow up at [PII_EMAIL] shortly."

    # --- Standard Dummy Logic ---
    # Very naive heuristics to simulate analysis or generation
    if "output only json" in system.lower() or "output only json" in prompt.lower():
        # To avoid being influenced by few-shot examples, only analyze the actual review text.
        # We find the text following "Review:" in the prompt.
        review_text_to_analyze = prompt
        if "Review:" in prompt:
            # Split on "Review:" and take the last part, which is the actual review.
            review_text_to_analyze = prompt.split("Review:")[-1]

        text_lower = review_text_to_analyze.lower()

        sentiment_keywords = DUMMY_LLM_KEYWORDS.get("sentiments", {})
        issue_keywords = DUMMY_LLM_KEYWORDS.get("issues", {})

        # simulate analysis JSON
        sentiment = "neutral"
        if any(w in text_lower for w in sentiment_keywords.get("positive", [])):
            sentiment = "positive"
        if any(w in text_lower for w in sentiment_keywords.get("negative", [])):
            sentiment = "negative"

        issues = []
        for issue, keywords in issue_keywords.items():
            if any(w in text_lower for w in keywords):
                issues.append(issue)
        if sentiment == "positive":
            issues.append("good product quality")
        summary = "Customer feedback: " + (" ".join(issues) if issues else "general feedback.")
        out = {
            "sentiment": sentiment,
            "key_issues_praise": issues,
            "summary": summary[:250],
        }
        return json.dumps(out)

    text_lower = prompt.lower()
    # Response generation dummy
    if "customer care" in system.lower() or "customercarebot" in system.replace(" ", "").lower():
        # produce a short empathetic reply
        if "sentiment: negative" in text_lower or "broken" in text_lower or "damaged" in text_lower or "ruined" in text_lower:
            return "We're very sorry your item arrived damaged. We want to make this right—please allow us to arrange a replacement or refund. Thank you for bringing this to our attention."
        if "sentiment: positive" in text_lower or "love" in text_lower or "works perfectly" in text_lower or "fantastic" in text_lower:
            return "Thank you! We're thrilled to hear you love your new product. If you have tips to share, we'd appreciate it."
        if "wants refund" in text_lower:
            return "We're sorry to hear you're disappointed with the product. We've made a note of your feedback and will process your return."
        return "Thank you for your feedback. We're here to help—please reach out so we can assist further."
    # default safe fallback
    return "Thank you for your review. We appreciate your feedback."
