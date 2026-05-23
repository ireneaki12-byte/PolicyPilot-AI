import sys
import time
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))

from rag_pipeline import answer_question


def evaluate():
    df = pd.read_csv("evaluation/eval_questions.csv")

    results = []

    for _, row in df.iterrows():
        question = row["question"]
        expected_source = row["expected_source"]

        start = time.time()
        response = answer_question(question)
        end = time.time()

        latency = end - start
        answer = response["answer"]
        citations = response["citations"]

        citation_sources = [c["source"] for c in citations]

        citation_match = (
            expected_source == "N/A"
            or expected_source in citation_sources
        )

        groundedness_manual_score = ""
        citation_accuracy_manual_score = ""

        results.append(
            {
                "id": row["id"],
                "question": question,
                "gold_answer": row["gold_answer"],
                "generated_answer": answer,
                "expected_source": expected_source,
                "retrieved_sources": citation_sources,
                "citation_match_auto": citation_match,
                "latency_seconds": latency,
                "groundedness_manual_score": groundedness_manual_score,
                "citation_accuracy_manual_score": citation_accuracy_manual_score,
            }
        )

    results_df = pd.DataFrame(results)
    results_df.to_csv("evaluation/evaluation_results.csv", index=False)

    print(results_df)
    print("\nEvaluation completed.")
    print("Results saved to evaluation/evaluation_results.csv")


if __name__ == "__main__":
    evaluate()