import io
from pathlib import Path

from groq import Groq

from config import STT_MODEL, require_groq_key

AGRI_PROMPT = (
    "Farmer question about cotton (pratti panta), paddy, groundnut, chilli, tomato. "
    "Telugu words: pratti panta cotton, aakulu leaves, yellow colour, em cheyyali."
)


def transcribe_audio_bytes(
    audio_bytes: bytes,
    filename: str = "question.wav",
    language: str | None = None,
) -> dict:
    client = Groq(api_key=require_groq_key(), timeout=60.0)
    kwargs = {
        "file": (filename, audio_bytes),
        "model": STT_MODEL,
        "response_format": "verbose_json",
        "temperature": 0,
        "prompt": AGRI_PROMPT,
    }
    if language in {"en", "hi", "te"}:
        kwargs["language"] = language
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
