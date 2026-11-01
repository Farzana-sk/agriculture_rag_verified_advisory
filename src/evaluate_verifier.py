"""Evaluate the verifier: WITH verification vs WITHOUT (plain RAG baseline).

Uses exactly the same steps as the live pipeline (retrieve -> generate -> verify
with k=RETRIEVE_K and the per-source scores). Expected verdicts come from
data/test_questions.csv:
  PASS     = answer exists in the knowledge base (should be released)
  REJECT   = not in the knowledge base (should be refused)
  BOUNDARY = partly covered; reported separately, not counted in accuracy

Run:  python src\\evaluate_verifier.py
      python src\\evaluate_verifier.py data\\test_questions_telugu.csv   (uses the English search query column "question" as-is)
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from .config import EVAL_RESULTS_CSV, RETRIEVE_K, TAU_THRESHOLD, TEST_QUESTIONS_CSV
    from .generate import generate_answer
    from .retrieve import build_context, retrieve_documents
    from .verify import verify_answer
except ImportError:  # pragma: no cover - script execution support
    from config import EVAL_RESULTS_CSV, RETRIEVE_K, TAU_THRESHOLD, TEST_QUESTIONS_CSV
    from generate import generate_answer
    from retrieve import build_context, retrieve_documents
    from verify import verify_answer


def summarize(df: pd.DataFrame, tau: float) -> dict:
    """Counts at one threshold, using only PASS/REJECT-labelled rows."""
    labelled = df[df["expected_verdict"].isin(["PASS", "REJECT"])]
    answerable = labelled[labelled["expected_verdict"] == "PASS"]
    unanswerable = labelled[labelled["expected_verdict"] == "REJECT"]
    released = labelled["tau_score"] >= tau
    good_release = int((released & (labelled["expected_verdict"] == "PASS")).sum())
    unsafe_release = int((released & (labelled["expected_verdict"] == "REJECT")).sum())
    false_reject = int((~released & (labelled["expected_verdict"] == "PASS")).sum())
    correct_refusal = int((~released & (labelled["expected_verdict"] == "REJECT")).sum())
    total = len(labelled)
    return {
        "tau": tau,
        "accuracy": (good_release + correct_refusal) / total if total else 0.0,
        "unsafe_release_rate": unsafe_release / len(unanswerable) if len(unanswerable) else 0.0,
        "false_reject_rate": false_reject / len(answerable) if len(answerable) else 0.0,
        "unsafe_release": unsafe_release,
        "false_reject": false_reject,
    }


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else TEST_QUESTIONS_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing evaluation file: {csv_path}")

    df = pd.read_csv(csv_path)
    rows = []
    for _, row in df.iterrows():
        query = row["question"]
        sources = retrieve_documents(query, k=RETRIEVE_K)
        context = build_context(sources)
        # No try/except on purpose: a missing key or API error must STOP the run,
        # not silently write junk rows into the results.
        answer = generate_answer(query, context)
        verification = verify_answer(answer, context, TAU_THRESHOLD, sources)
        expected = str(row["expected_verdict"]).upper()
        rows.append(
            {
                "id": row["id"],
                "question": query,
                "category": row["category"],
                "expected_verdict": expected,
                "tau_score": verification["trust_score"],
                "actual_verdict": verification["verdict"],
                "aligned": True if expected == "BOUNDARY" else verification["verdict"] == expected,
                "top_source": sources[0]["file"] if sources else "",
                "generated_answer": answer,
            }
        )
        print(f"{row['id']}: {verification['verdict']} (score={verification['trust_score']}) expected={expected}")

    results = pd.DataFrame(rows)
    EVAL_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(EVAL_RESULTS_CSV, index=False)

    labelled = results[results["expected_verdict"].isin(["PASS", "REJECT"])]
    answerable = labelled[labelled["expected_verdict"] == "PASS"]
    unanswerable = labelled[labelled["expected_verdict"] == "REJECT"]
    boundary = results[results["expected_verdict"] == "BOUNDARY"]

    with_v = summarize(results, TAU_THRESHOLD)
    print("\n=== WITHOUT verification (plain RAG: every answer is released) ===")
    print(f"Unsafe releases (answers for questions NOT in the KB): {len(unanswerable)}/{len(unanswerable)} = 100.0%")
    print("False rejects: 0")
    print(f"\n=== WITH verification (tau = {TAU_THRESHOLD:.2f}) ===")
    print(f"Accuracy (PASS/REJECT rows): {with_v['accuracy']:.1%} of {len(labelled)}")
    print(f"Unsafe releases: {with_v['unsafe_release']}/{len(unanswerable)} = {with_v['unsafe_release_rate']:.1%}")
    print(f"False rejects:   {with_v['false_reject']}/{len(answerable)} = {with_v['false_reject_rate']:.1%}")
    if len(boundary):
        released = int((boundary["tau_score"] >= TAU_THRESHOLD).sum())
        print(f"BOUNDARY rows: {released}/{len(boundary)} released (not counted in accuracy)")

    print("\n=== Score separation ===")
    print(f"Mean trust score, answerable questions:   {answerable['tau_score'].mean():.3f}")
    print(f"Mean trust score, unanswerable questions: {unanswerable['tau_score'].mean():.3f}")
    try:
        from sklearn.metrics import roc_auc_score

        auc = roc_auc_score((labelled["expected_verdict"] == "PASS").astype(int), labelled["tau_score"])
        print(f"ROC-AUC of the cosine score: {auc:.3f}  (0.5 = no better than a coin flip, 1.0 = perfect)")
    except Exception as exc:  # only one class present, etc.
        print(f"ROC-AUC not computed: {exc}")

    print("\n=== Threshold sweep (same scores, no extra LLM calls) ===")
    print("tau   accuracy  unsafe_release  false_reject")
    best = None
    for tau in [round(0.40 + 0.05 * i, 2) for i in range(10)]:
        s = summarize(results, tau)
        print(f"{tau:.2f}  {s['accuracy']:7.1%}   {s['unsafe_release_rate']:12.1%}  {s['false_reject_rate']:12.1%}")
        balanced = 1 - (s["unsafe_release_rate"] + s["false_reject_rate"]) / 2
        if best is None or balanced > best[0]:
            best = (balanced, tau)
    print(f"Best tau by balanced error: {best[1]:.2f}")
    print(f"\nResults written to: {EVAL_RESULTS_CSV}")


if __name__ == "__main__":
    main()