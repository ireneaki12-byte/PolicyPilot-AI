import re
import sys
import time
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app"
EVAL_INPUT_PATH = PROJECT_ROOT / "evaluation" / "eval_questions.csv"
EVAL_OUTPUT_PATH = PROJECT_ROOT / "evaluation" / "evaluation_results.csv"

# Allow imports from the app folder
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(APP_PATH))

try:
    from app.rag_pipeline import answer_question
except ImportError:
    from rag_pipeline import answer_question  # noqa: E402


def normalize_text(text: str) -> str:
    """
    Normalize text for fair comparison.

    This removes punctuation, converts text to lowercase,
    and removes extra spaces.
    """
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def calculate_exact_match(gold_answer: str, generated_answer: str) -> int:
    """
    Return 1 if the normalized generated answer exactly matches
    the normalized gold answer. Otherwise return 0.
    """
    gold = normalize_text(gold_answer)
    generated = normalize_text(generated_answer)

    return 1 if gold == generated else 0


def calculate_partial_match(gold_answer: str, generated_answer: str) -> float:
    """
    Calculate a simple partial match score based on word overlap.

    Scoring:
    1   = strong overlap
    0.5 = moderate overlap
    0   = weak or no overlap
    """
    gold_words = set(normalize_text(gold_answer).split())
    generated_words = set(normalize_text(generated_answer).split())

    if not gold_words:
        return 0

    overlap = gold_words.intersection(generated_words)
    overlap_ratio = len(overlap) / len(gold_words)

    if overlap_ratio >= 0.70:
        return 1
    elif overlap_ratio >= 0.40:
        return 0.5
    else:
        return 0


def calculate_latency(start_time: float, end_time: float) -> float:
    """Return latency rounded to 3 decimal places."""
    return round(end_time - start_time, 3)


def extract_citation_sources(citations: list[dict]) -> list[str]:
    """Extract source filenames from citation objects."""
    return [citation.get("source", "Unknown source") for citation in citations]


def check_citation_match(expected_source: str, citation_sources: list[str]) -> bool:
    """
    Check whether the expected source appears in the retrieved citation sources.

    For out-of-scope questions, expected_source may be N/A.
    """
    if expected_source == "N/A":
        return True

    return expected_source in citation_sources


def evaluate_question(row: pd.Series) -> dict:
    """Run one evaluation question through the RAG pipeline."""
    question = row["question"]
    gold_answer = row["gold_answer"]
    expected_source = row["expected_source"]

    start_time = time.time()
    response = answer_question(question)
    end_time = time.time()

    generated_answer = response.get("answer", "")
    citations = response.get("citations", [])
    snippets = response.get("snippets", [])

    citation_sources = extract_citation_sources(citations)
    citation_match = check_citation_match(expected_source, citation_sources)
    latency_seconds = calculate_latency(start_time, end_time)

    exact_match_score = calculate_exact_match(gold_answer, generated_answer)
    partial_match_score = calculate_partial_match(gold_answer, generated_answer)

    return {
        "id": row["id"],
        "question": question,
        "gold_answer": gold_answer,
        "generated_answer": generated_answer,
        "expected_source": expected_source,
        "retrieved_sources": citation_sources,
        "retrieved_snippets": snippets,
        "citation_match_auto": citation_match,
        "exact_match_score": exact_match_score,
        "partial_match_score": partial_match_score,
        "latency_seconds": latency_seconds,
        "groundedness_manual_score": "",
        "citation_accuracy_manual_score": "",
    }


def evaluate() -> None:
    """Run evaluation and save results to CSV."""
    if not EVAL_INPUT_PATH.exists():
        raise FileNotFoundError(f"Evaluation file not found: {EVAL_INPUT_PATH}")

    df = pd.read_csv(EVAL_INPUT_PATH)

    required_columns = {"id", "question", "gold_answer", "expected_source"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    results = []

    print(f"Running evaluation for {len(df)} questions...\n")

    for _, row in df.iterrows():
        print(f"Evaluating question {row['id']}: {row['question']}")
        result = evaluate_question(row)
        results.append(result)

    results_df = pd.DataFrame(results)
    results_df.to_csv(EVAL_OUTPUT_PATH, index=False)

    print("\nEvaluation completed.")
    print(f"Results saved to: {EVAL_OUTPUT_PATH}")

    print("\nLatency Summary:")
    print(f"p50 latency: {results_df['latency_seconds'].quantile(0.50):.3f} seconds")
    print(f"p95 latency: {results_df['latency_seconds'].quantile(0.95):.3f} seconds")

    print("\nExact / Partial Match Summary:")
    print(f"Exact match: {results_df['exact_match_score'].mean() * 100:.1f}%")
    print(f"Partial match: {results_df['partial_match_score'].mean() * 100:.1f}%")

    print("\nCitation Match Summary:")
    print(f"Automatic citation match: {results_df['citation_match_auto'].mean() * 100:.1f}%")

    print("\nNext step:")
    print("Open evaluation/evaluation_results.csv and manually fill:")
    print("- groundedness_manual_score")
    print("- citation_accuracy_manual_score")


if __name__ == "__main__":
    evaluate()