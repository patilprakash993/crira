import os
from analysis_engine import analyze_review


def test_safe_mode_redacts_pii_by_default():
    """
    Tests that in default SAFE_MODE, PII is redacted.
    """
    review_with_pii = "My email is test@example.com."
    analyzed = analyze_review(review_with_pii)
    assert "\\[PII_EMAIL\\]" in analyzed["redacted_review"]
    assert "test@example.com" not in analyzed["redacted_review"]
    assert "PII_EMAIL" in analyzed["pii_found"]


def test_unsafe_mode_does_not_redact_pii(monkeypatch):
    """
    Tests that when CRIRA_SAFE_MODE is 'false', PII is NOT redacted.
    """
    monkeypatch.setenv("CRIRA_SAFE_MODE", "false")
    review_with_pii = "My email is test@example.com."
    analyzed = analyze_review(review_with_pii)
    assert "[PII_EMAIL]" not in analyzed["redacted_review"]
    assert "test@example.com" in analyzed["redacted_review"]
    assert not analyzed["pii_found"]