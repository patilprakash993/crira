
import os
from analysis_engine import analyze_review
from response_generator import generate_response


def test_critical_ref_appended_for_urgent_review():
    review = "This is urgent! My package is missing and I need immediate action ASAP."
    analyzed = analyze_review(review)
    resp = generate_response(analyzed, review)
    assert resp["is_critical"] is True
    # critical_ref should be a backend-generated string when SAFE_MODE True
    assert resp["critical_ref"] is not None
    assert resp["critical_ref"].startswith("[CRITICAL_REF:")


def test_non_critical_review_has_no_critical_ref():
    review = "I love the product. Great quality."
    analyzed = analyze_review(review)
    resp = generate_response(analyzed, review)
    assert resp["is_critical"] is False
    assert resp["critical_ref"] is None
