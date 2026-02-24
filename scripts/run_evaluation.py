"""
Run RAG evaluation against data/evaluation_questions.json.

Reports groundedness (answer supported by retrieved context) and
citation accuracy (Policy ID present in sources). Logs p50/p95 latency.

Usage (after building vector store and setting up LLM):
  PYTHONPATH=. python scripts/run_evaluation.py
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_questions(path: str = "data/evaluation_questions.json") -> list:
    """Load evaluation questions from JSON."""
    with open(Path(path).resolve(), encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


def _parse_policy_hints(policy_hint: str) -> list[str]:
    """Split 'VL-SEC-013 or VL-SEC-019' into ['vl-sec-013', 'vl-sec-019'] for flexible citation check."""
    if not policy_hint or not isinstance(policy_hint, str):
        return []
    parts = [p.strip().lower() for p in policy_hint.replace(" and ", " or ").split(" or ") if p.strip()]
    return parts


def evaluate_groundedness_and_citation(
    result: dict, expected_terms: list, policy_hint: str
) -> tuple[bool, bool]:
    """
    Check if answer is grounded (contains expected terms) and cites policy.

    Policy hints like "VL-SEC-013 or VL-SEC-019" are split; citation passes if any hint is present.

    Returns:
        (grounded: bool, cited: bool)
    """
    answer = (result.get("answer") or "").lower()
    sources = [s.lower() for s in result.get("sources", [])]
    hints = _parse_policy_hints(policy_hint or "")
    expected = list(expected_terms) if expected_terms else []
    grounded = all(term.lower() in answer for term in expected) if expected else True
    cited = any(h in sources or h in answer for h in hints) if hints else False
    return grounded, cited


def run_evaluation(engine, questions_path: str = "data/evaluation_questions.json") -> dict:
    """
    Run RAG on each evaluation question and aggregate metrics.

    Args:
        engine: RAGEngine instance (vector_store + LLM already injected).
        questions_path: Path to evaluation_questions.json.

    Returns:
        Dict with groundedness_pct, citation_accuracy_pct, p50_ms, p95_ms, details.
    """
    questions = load_questions(questions_path)
    grounded_ok = 0
    citation_ok = 0
    details = []
    failed_grounded: list[str] = []
    failed_cited: list[str] = []
    processed = 0
    for q in questions:
        question_text = q.get("question")
        if not question_text:
            logger.warning("Skipping question with missing 'question' key: %s", q.get("id", "?"))
            continue
        r = engine.ask(question_text, k=4)
        expected_terms = q.get("expected_terms")
        if expected_terms is None:
            expected_terms = []
        policy_hint = q.get("policy_hint", "")
        grounded, cited = evaluate_groundedness_and_citation(r, expected_terms, policy_hint)
        qid = q.get("id", "?")
        processed += 1
        if grounded:
            grounded_ok += 1
        else:
            failed_grounded.append(qid)
        if cited:
            citation_ok += 1
        else:
            failed_cited.append(qid)
        details.append({"id": qid, "grounded": grounded, "cited": cited})
    n = processed or 1
    from src.rag_engine import get_latency_percentiles
    percentiles = get_latency_percentiles()
    report = {
        "groundedness_pct": round(100 * grounded_ok / n, 1),
        "citation_accuracy_pct": round(100 * citation_ok / n, 1),
        "p50_ms": percentiles.get("p50_ms"),
        "p95_ms": percentiles.get("p95_ms"),
        "n_questions": len(questions),
        "n_processed": processed,
        "details": details,
    }
    logger.info(
        "Groundedness: %.1f%% | Citation accuracy: %.1f%% | p50_ms: %s | p95_ms: %s",
        report["groundedness_pct"], report["citation_accuracy_pct"],
        report["p50_ms"], report["p95_ms"],
    )
    if failed_grounded:
        logger.info("Questions missing expected terms (not grounded): %s", ", ".join(failed_grounded))
    if failed_cited:
        logger.info("Questions missing policy citation: %s", ", ".join(failed_cited))
    return report


if __name__ == "__main__":
    import sys
    questions_path = "data/eval_20_gold.json"
    if len(sys.argv) > 1:
        questions_path = sys.argv[1]
    from src.rag_app import get_engine
    engine = get_engine()
    report = run_evaluation(engine, questions_path=questions_path)
    print(json.dumps(report, indent=2))
