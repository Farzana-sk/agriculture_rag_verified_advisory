import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from .config import EVAL_RESULTS_CSV, TEST_QUESTIONS_CSV, TAU_THRESHOLD
    from .generate import generate_answer
    from .retrieve import build_context, retrieve_documents
    from .verify import verify_answer
except ImportError:  # pragma: no cover - script execution support
    from config import EVAL_RESULTS_CSV, TEST_QUESTIONS_CSV, TAU_THRESHOLD
    from generate import generate_answer
    from retrieve import build_context, retrieve_documents
    from verify import verify_answer


def main() -> None:
    if not TEST_QUESTIONS_CSV.exists():
        raise FileNotFoundError(f"Missing evaluation file: {TEST_QUESTIONS_CSV}")

    df = pd.read_csv(TEST_QUESTIONS_CSV)
    results = []

    for _, row in df.iterrows():
        query = row["question"]
        sources = retrieve_documents(query, k=4)
        context = build_context(sources)
        answer = generate_answer(query, context)
        verification = verify_answer(answer, context, TAU_THRESHOLD)
        expected = str(row["expected_verdict"]).upper()
        actual = verification["verdict"]
        aligned = True if expected == "BOUNDARY" else actual == expected

        results.append(
            {
                "id": row["id"],
                "question": query,
                "category": row["category"],
                "generated_answer": answer,
                "tau_score": verification["trust_score"],
                "actual_verdict": actual,
                "expected_verdict": expected,
                "aligned": aligned,
            }
        )
        print(f"{row['id']}: {actual} (score={verification['trust_score']}) expected={expected}")

    results_df = pd.DataFrame(results)
    EVAL_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(EVAL_RESULTS_CSV, index=False)

    total = len(results_df)
    accuracy = float(results_df["aligned"].mean()) if total else 0.0
    pass_count = int((results_df["actual_verdict"] == "PASS").sum())
    reject_count = int((results_df["actual_verdict"] == "REJECT").sum())

    print("\n--- EVALUATION SUMMARY ---")
    print(f"Total test cases: {total}")
    print(f"Approved (tau >= {TAU_THRESHOLD:.2f}): {pass_count}")
    print(f"Blocked (tau < {TAU_THRESHOLD:.2f}): {reject_count}")
    print(f"Verdict alignment accuracy: {accuracy:.2%}")
    print(f"Results written to: {EVAL_RESULTS_CSV}")


if __name__ == "__main__":
    main()
