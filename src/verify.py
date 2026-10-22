from sklearn.metrics.pairwise import cosine_similarity

from config import TAU_THRESHOLD
from embeddings import get_embedding_model


def cosine_trust_score(answer: str, context: str) -> float:
    if not answer.strip() or not context.strip():
        return 0.0
    model = get_embedding_model()
    answer_vec = model.embed_query(answer[:1500])
    context_vec = model.embed_query(context[:2500])
    return float(cosine_similarity([answer_vec], [context_vec])[0][0])


def verify_answer(
    answer: str,
    context: str,
    tau: float = TAU_THRESHOLD,
    sources: list[dict] | None = None,
) -> dict:
    scores = [cosine_trust_score(answer, context)]
    for source in sources or []:
        snippet = (source.get("snippet") or "").strip()
        if snippet:
            scores.append(cosine_trust_score(answer, snippet))
    score = max(scores) if scores else 0.0
    verdict = "PASS" if score >= tau else "REJECT"
    return {
        "trust_score": round(score, 4),
        "verdict": verdict,
        "tau": tau,
    }
