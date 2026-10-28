from sklearn.metrics.pairwise import cosine_similarity

try:
    from .config import TAU_THRESHOLD
    from .embeddings import get_embedding_model
except ImportError:  # pragma: no cover - script execution support
    from config import TAU_THRESHOLD
    from embeddings import get_embedding_model


def _as_text(value: str | None) -> str:
    return "" if value is None else str(value)


def cosine_trust_score(answer: str, context: str) -> float:
    answer_text = _as_text(answer).strip()
    context_text = _as_text(context).strip()
    if not answer_text or not context_text:
        return 0.0
    model = get_embedding_model()
    answer_vec = model.embed_query(answer_text[:1500])
    context_vec = model.embed_query(context_text[:2500])
    return float(cosine_similarity([answer_vec], [context_vec])[0][0])


def verify_answer(
    answer: str,
    context: str,
    tau: float = TAU_THRESHOLD,
    sources: list[dict] | None = None,
) -> dict:
    answer_text = _as_text(answer)
    context_text = _as_text(context)
    scores = [cosine_trust_score(answer_text, context_text)]
    for source in sources or []:
        snippet = _as_text(source.get("snippet") if isinstance(source, dict) else source).strip()
        if snippet:
            scores.append(cosine_trust_score(answer_text, snippet))
    score = max(scores) if scores else 0.0
    verdict = "PASS" if score >= tau else "REJECT"
    return {
        "trust_score": round(score, 4),
        "verdict": verdict,
        "tau": tau,
    }
