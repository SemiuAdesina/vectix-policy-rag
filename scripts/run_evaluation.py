"""
Run a simple evaluation pass for the policy RAG app.

Usage:
  PYTHONPATH=. python scripts/run_evaluation.py
"""

import json
import logging
import re
from pathlib import Path

from src.reproducibility import set_reproducible_seed

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NORMALIZATION_RULES = [
    (re.compile(r"\bmulti[- ]factor(?: authentication)?\b"), "mfa"),
    (re.compile(r"\boctober\b"), "oct"),
    (re.compile(r"\bminutes\b"), "minute"),
    (re.compile(r"\bhours\b"), "hour"),
]
NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "twenty": "20",
}


def load_questions(path: str = "data/eval_20_gold.json") -> list[dict]:
    """Load evaluation prompts from disk."""
    with open(Path(path).resolve(), encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("questions", [])


def _parse_policy_hints(policy_hint: str) -> list[str]:
    """Normalize flexible policy hint strings like 'A or B'."""
    if not policy_hint or not isinstance(policy_hint, str):
        return []
    normalized = policy_hint.replace(" and ", " or ").lower()
    return [part.strip() for part in normalized.split(" or ") if part.strip()]


def _normalize_phrase(text: str) -> str:
    """Normalize small wording variants used in the evaluation set."""
    normalized = text.lower()
    for source, target in NUMBER_WORDS.items():
        normalized = re.sub(rf"\b{source}\b", target, normalized)
    for pattern, replacement in NORMALIZATION_RULES:
        normalized = pattern.sub(replacement, normalized)
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def evaluate_groundedness_and_citation(
    result: dict,
    expected_terms: list[str],
    policy_hint: str,
) -> tuple[bool, bool]:
    """Score one answer with simple string checks."""
    answer = _normalize_phrase(result.get("answer") or "")
    sources = [_normalize_phrase(source) for source in result.get("sources", [])]
    expected = expected_terms or []
    hints = _parse_policy_hints(policy_hint)
    normalized_expected = list(dict.fromkeys(_normalize_phrase(term) for term in expected if term))
    normalized_hints = [_normalize_phrase(hint) for hint in hints]
    grounded = all(term in answer for term in normalized_expected) if normalized_expected else True
    cited = any(hint in sources or hint in answer for hint in normalized_hints) if normalized_hints else False
    return grounded, cited


def run_evaluation(engine, questions_path: str = "data/eval_20_gold.json") -> dict:
    """Run the full evaluation set and aggregate metrics."""
    seed = set_reproducible_seed()
    logger.info("Using reproducible seed %s", seed)
    questions = load_questions(questions_path)
    grounded_ok = 0
    citation_ok = 0
    processed = 0
    details = []

    for question in questions:
        prompt = question.get("question")
        if not prompt:
            logger.warning("Skipping malformed question entry: %s", question.get("id", "?"))
            continue

        result = engine.ask(prompt, k=4)
        grounded, cited = evaluate_groundedness_and_citation(
            result=result,
            expected_terms=question.get("expected_terms") or [],
            policy_hint=question.get("policy_hint", ""),
        )

        processed += 1
        grounded_ok += int(grounded)
        citation_ok += int(cited)
        details.append({"id": question.get("id", "?"), "grounded": grounded, "cited": cited})

    from src.rag_engine import get_latency_percentiles

    percentiles = get_latency_percentiles()
    denominator = processed or 1
    report = {
        "groundedness_pct": round(100 * grounded_ok / denominator, 1),
        "citation_accuracy_pct": round(100 * citation_ok / denominator, 1),
        "p50_ms": percentiles.get("p50_ms"),
        "p95_ms": percentiles.get("p95_ms"),
        "n_questions": len(questions),
        "n_processed": processed,
        "details": details,
    }
    logger.info(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    import sys

    questions_path = sys.argv[1] if len(sys.argv) > 1 else "data/eval_20_gold.json"
    from src.rag_app import get_engine

    engine = get_engine()
    report = run_evaluation(engine, questions_path=questions_path)
    print(json.dumps(report, indent=2))
