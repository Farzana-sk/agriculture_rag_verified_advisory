from groq import Groq

from config import LLM_MODEL, require_groq_key

SYSTEM_PROMPT = (
    "You are an agricultural advisory assistant grounded in official "
    "Package of Practices documents. Use only the provided context. "
    "Never invent pesticide names, doses, or spray schedules. "
    "If the farmer asks for pesticides but the context only has varieties "
    "or pest-tolerance notes, say that clearly and quote those facts. "
    "Do not claim a chemical recommendation that is not written in the context."
)


def generate_answer(question: str, context: str) -> str:
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
    return text
