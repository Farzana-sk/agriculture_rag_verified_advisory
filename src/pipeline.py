try:
    from .config import SAFE_REFUSAL, TAU_THRESHOLD
    from .db import save_advisory
    from .generate import generate_answer
    from .language import (
        detect_language,
        prepare_speech_text,
        rewrite_to_english,
        spoken_summary,
        translate_answer,
    )
    from .retrieve import build_context, retrieve_documents
    from .verify import verify_answer
except ImportError:  # pragma: no cover - script execution support
    from config import SAFE_REFUSAL, TAU_THRESHOLD
    from db import save_advisory
    from generate import generate_answer
    from language import (
        detect_language,
        prepare_speech_text,
        rewrite_to_english,
        spoken_summary,
        translate_answer,
    )
    from retrieve import build_context, retrieve_documents
    from verify import verify_answer

REFUSALS = {
    "en": SAFE_REFUSAL,
    "hi": (
        "कृषि ज्ञान आधार में पर्याप्त आधिकारिक जानकारी नहीं है। "
        "इस प्रश्न के लिए सत्यापित सिफारिश नहीं दी जा सकती।"
    ),
    "te": (
        "అధికారిక వ్యవసాయ పత్రాల్లో ఈ ప్రశ్నకు సరిపోయే సమాచారం లేదు. "
        "ధృవీకరించిన సిఫారసు ఇవ్వలేము."
    ),
}

AGRI_HINTS = (
    "cotton",
    "paddy",
    "rice",
    "groundnut",
    "tomato",
    "chilli",
    "chili",
    "leaf",
    "leaves",
    "pest",
    "pesticide",
    "fertilizer",
    "variety",
    "varieties",
    "yellow",
    "crop",
    "pratti",
    "panta",
    "vari",
    "rakalu",
    "aakulu",
    "jassid",
    "nursery",
    "vegetable",
)


def is_agriculture_query(question: str, search_query: str) -> bool:
    blob = f"{question} {search_query}".lower()
    return any(hint in blob for hint in AGRI_HINTS)


def run_advisory(question: str, language: str | None = None) -> dict:
    question = (question or "").strip()
    if not question:
        raise ValueError("Question text is empty.")

    # Farmer question language wins. "vari rakalu emiti?" is Telugu even if
    # the dropdown is English.
    output_lang = detect_language(question, language)
    search_query = question if output_lang == "en" else rewrite_to_english(question)
    sources = retrieve_documents(search_query)
    context = build_context(sources)
    generated = generate_answer(search_query, context)
    verification = verify_answer(generated, context, TAU_THRESHOLD, sources)

    agri = is_agriculture_query(question, search_query)
    if verification["verdict"] == "PASS":
        english_answer = generated
    elif agri and generated:
        english_answer = generated
    else:
        english_answer = REFUSALS["en"]

    if output_lang in {"te", "hi"}:
        final_answer = translate_answer(english_answer, output_lang)
    else:
        final_answer = english_answer

    result = {
        "question": question,
        "search_query": search_query,
        "language": output_lang,
        "generated_answer": generated,
        "final_answer": final_answer,
        "speech_text": spoken_summary(final_answer, output_lang),
        "answer": final_answer,
        "trust_score": verification["trust_score"],
        "verdict": verification["verdict"],
        "tau": verification["tau"],
        "sources": sources,
    }
    result["id"] = save_advisory(result)
    return result
