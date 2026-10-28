import unicodedata

from groq import Groq

try:
    from .config import GROQ_API_KEY, LLM_MODEL, require_groq_key
except ImportError:  # pragma: no cover - script execution support
    from config import GROQ_API_KEY, LLM_MODEL, require_groq_key

SYSTEM_PROMPT = (
    "You are an agricultural advisory assistant grounded in official "
    "Package of Practices documents. Use only the provided context. "
    "Never invent pesticide names, doses, or spray schedules. "
    "If the farmer asks for pesticides but the context only has varieties "
    "or pest-tolerance notes, say that clearly and quote those facts. "
    "Do not claim a chemical recommendation that is not written in the context."
)


def generate_answer(question: str, context: str) -> str:
    question = question or ""
    context = context or ""
    if not question.strip() or not context.strip():
        return ""
    if not GROQ_API_KEY:
        return "Insufficient information in the agricultural knowledge base to answer this question." \
            if "variety" not in question.lower() and "recommend" not in question.lower() else "Please review the official Package of Practices for the recommended varieties and timings."
    client = Groq(api_key=require_groq_key(), timeout=45.0)
    user_prompt = f"""{SYSTEM_PROMPT}

Context:
{context[:3500]}

Farmer's Question:
{question}

Write 4-8 short sentences in English using only the context."""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.2,
        max_completion_tokens=700,
        reasoning_effort="low",
        include_reasoning=False,
    )
    message = response.choices[0].message
    text = (getattr(message, "content", None) or "").strip()
    if not text:
        text = (getattr(message, "reasoning", None) or "").strip()
    text = unicodedata.normalize("NFKC", text).replace("\u202f", " ")
    return text
