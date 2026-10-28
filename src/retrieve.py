from pathlib import Path

try:
    from .config import RETRIEVE_K
    from .embeddings import get_vector_store
except ImportError:  # pragma: no cover - script execution support
    from config import RETRIEVE_K
    from embeddings import get_vector_store

CROP_FILES = {
    "cotton": "cotton.pdf",
    "pratti": "cotton.pdf",
    "prathi": "cotton.pdf",
    "paddy": "paddy.pdf",
    "rice": "paddy.pdf",
    "vari": "paddy.pdf",
    "groundnut": "groundnut.pdf",
    "peanut": "groundnut.pdf",
    "tomato": "pop_veg_culti (1).pdf",
    "chilli": "pop_veg_culti (1).pdf",
    "chili": "pop_veg_culti (1).pdf",
    "brinjal": "pop_veg_culti (1).pdf",
    "vegetable": "pop_veg_culti (1).pdf",
    "nursery": "pop_veg_culti (1).pdf",
    "bhendi": "pop_veg_culti (1).pdf",
    "okra": "pop_veg_culti (1).pdf",
    "coconut": "pop_hf.pdf",
    "arecanut": "pop_hf.pdf",
    "mango": "pop_hf.pdf",
    "banana": "pop_hf.pdf",
}


def _is_boilerplate(text: str) -> bool:
    lowered = text.lower()
    if len(text.strip()) < 80:
        return True
    cover_markers = (
        "published by",
        "prepared by",
        "training manual",
        "central agricultural research institute",
        "central island agricultural research institute",
    )
    if sum(marker in lowered for marker in cover_markers) >= 2:
        return True
    if "package of practices" in lowered and len(text) < 350:
        return True
    return False


def _preferred_files(query: str) -> set[str]:
    lowered = query.lower()
    return {filename for crop, filename in CROP_FILES.items() if crop in lowered}


def retrieve_documents(query: str, k: int = RETRIEVE_K) -> list[dict]:
    vector_db = get_vector_store()
    scored_docs = vector_db.similarity_search_with_score(query, k=max(k * 4, 16))
    preferred = _preferred_files(query)

    ranked = []
    seen = set()
    for doc, distance in scored_docs:
        snippet = doc.page_content.strip()
        fingerprint = snippet[:160].lower()
        if fingerprint in seen or _is_boilerplate(snippet):
            continue
        seen.add(fingerprint)

        source = Path(str(doc.metadata.get("source", "Unknown"))).name
        page = doc.metadata.get("page", "Unknown")
        if isinstance(page, int):
            page = page + 1

        score = float(distance)
        if preferred and source.lower() in preferred:
            score -= 0.35
        elif preferred:
            score += 0.12
        ranked.append(
            {
                "file": source,
                "page": page,
                "snippet": snippet,
                "score": score,
            }
        )

    ranked.sort(key=lambda item: item["score"])
    if preferred:
        filtered = [item for item in ranked if item["file"].lower() in preferred]
        if len(filtered) >= min(3, k):
            ranked = filtered

    results = []
    for item in ranked[:k]:
        item.pop("score", None)
        results.append(item)
    return results


def build_context(sources: list[dict]) -> str:
    parts = []
    for idx, src in enumerate(sources, start=1):
        parts.append(
            f"--- Source {idx}: {src['file']} (page {src['page']}) ---\n{src['snippet']}"
        )
    return "\n\n".join(parts)
