"""Simple CLI to run CRIRA analysis & response generation on a reviews JSON file."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

from analysis_engine import analyze_review
from response_generator import generate_response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def process_review(review_text: str) -> dict[str, Any]:
    analyzed = analyze_review(review_text)
    response = generate_response(analyzed, review_text)
    return {
        "original_review": review_text,
        "analyzed": analyzed,
        "response": response,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="CRIRA - Review analysis and response")
    parser.add_argument("--reviews", type=str, default="reviews.json", help="Path to reviews.json")
    parser.add_argument("--output", type=str, default="results.json", help="Output file")
    args = parser.parse_args()

    reviews_path = Path(args.reviews)
    if not reviews_path.exists():
        logger.error(f"Reviews file {reviews_path} not found.")
        return

    data = json.loads(reviews_path.read_text(encoding="utf-8"))
    results = []
    
    # The JSON is a dict with a 'reviews' key containing the list
    review_list = data.get("reviews", [])
    if not review_list:
        logger.warning("No 'reviews' key found in JSON file, or the list is empty.")
    for entry in review_list:
        review_text = entry.get("review_text", "") # Match key in reviews.json
        if not review_text:
            logger.warning("Skipping empty review entry.")
            continue
        try:
            summary = (review_text[:80] + "...") if len(review_text) > 80 else review_text
            logger.info("Processing review: %s", summary)
            r = process_review(review_text)
            results.append(r)
        except Exception:
            logger.exception("Failed to process review: %s", review_text)

    out_file = Path(args.output)
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote results to %s", out_file)


if __name__ == "__main__":
    main()
