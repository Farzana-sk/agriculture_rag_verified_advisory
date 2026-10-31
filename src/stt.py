import io
from pathlib import Path

from groq import Groq

try:
    from .config import STT_MODEL, require_groq_key
except ImportError:  # pragma: no cover - script execution support
    from config import STT_MODEL, require_groq_key

# The hint must be written in the SAME script as the speech. An English-letter
# hint pushes Whisper to answer in English/romanized text even for Telugu audio.
AGRI_PROMPTS = {
    "te": "వ్యవసాయ ప్రశ్న: పత్తి, వరి, వేరుశనగ, మిరప, టమాటా, వంకాయ, విత్తన మోతాదు, పంట కాలం, రకాలు.",
    "hi": "कृषि प्रश्न: कपास, धान, मूंगफली, मिर्च, टमाटर, बीज दर, फसल अवधि, किस्में।",
    "en": "Farmer question about cotton, paddy, groundnut, chilli, tomato, brinjal, seed rate, crop duration, varieties.",
}


def transcribe_audio_bytes(
    audio_bytes: bytes,
    filename: str = "question.wav",
    language: str | None = None,
) -> dict:
    if not audio_bytes:
        return {"text": "", "language": language or "en"}
    client = Groq(api_key=require_groq_key(), timeout=60.0)
    kwargs = {
        "file": (filename, audio_bytes),
        "model": STT_MODEL,
        "response_format": "verbose_json",
        "temperature": 0,
    }
    if language in {"en", "hi", "te"}:
        kwargs["language"] = language
        kwargs["prompt"] = AGRI_PROMPTS[language]
    # language is None ("Auto detect"): send no hint so Whisper detects freely.
    result = client.audio.transcriptions.create(**kwargs)
    text = (getattr(result, "text", None) or str(result)).strip()
    detected = getattr(result, "language", None)
    return {"text": text, "language": language or detected}


def transcribe_audio_file(path: str | Path, language: str | None = None) -> dict:
    audio_path = Path(path)
    return transcribe_audio_bytes(audio_path.read_bytes(), audio_path.name, language)


def record_and_transcribe(duration: int = 6, sample_rate: int = 16000, language: str | None = None) -> dict:
    import sounddevice as sd
    from scipy.io.wavfile import write

    print("\nSpeak your agricultural question...")
    print("Recording started...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    print("Recording finished.")

    buffer = io.BytesIO()
    write(buffer, sample_rate, audio)
    return transcribe_audio_bytes(buffer.getvalue(), "farmer_question.wav", language)