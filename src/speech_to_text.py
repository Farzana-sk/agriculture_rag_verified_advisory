import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from .stt import record_and_transcribe
except ImportError:  # pragma: no cover - script execution support
    from stt import record_and_transcribe


def transcribe_voice_question(duration: int = 5) -> str:
    result = record_and_transcribe(duration=duration)
    query = result["text"]
    print("\n--- TRANSCRIBED QUESTION ---")
    print(query)
    return query


if __name__ == "__main__":
    transcribe_voice_question()
