import asyncio
import io
import os
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor

try:
    from .language import prepare_speech_text, tts_lang_code
except ImportError:  # pragma: no cover - script execution support
    from language import prepare_speech_text, tts_lang_code

# Microsoft neural voices (edge-tts): one streaming request, much faster than gTTS.
# Change a voice without editing code: set TTS_VOICE_TE=te-IN-MohanNeural in .env
# Telugu: te-IN-ShrutiNeural (female), te-IN-MohanNeural (male)
# Hindi : hi-IN-SwaraNeural (female), hi-IN-MadhurNeural (male)
# English (India): en-IN-NeerjaNeural (female), en-IN-PrabhatNeural (male)
EDGE_VOICES = {
    "en": os.getenv("TTS_VOICE_EN", "en-IN-NeerjaNeural"),
    "te": os.getenv("TTS_VOICE_TE", "te-IN-ShrutiNeural"),
    "hi": os.getenv("TTS_VOICE_HI", "hi-IN-SwaraNeural"),
}
# Speaking speed per language. Telugu was too fast at +10%, so it is slowed.
SPEECH_RATES = {
    "en": os.getenv("TTS_RATE_EN", "+0%"),
    "te": os.getenv("TTS_RATE_TE", "-15%"),
    "hi": os.getenv("TTS_RATE_HI", "-5%"),
}


def _edge_tts_bytes(text: str, voice: str, rate: str) -> bytes:
    import edge_tts

    async def run() -> bytes:
        audio = bytearray()
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
        return bytes(audio)

    data = asyncio.run(run())
    if not data:
        raise RuntimeError("edge-tts returned no audio")
    return data


def _gtts_piece(piece: str, lang: str) -> bytes:
    from gtts import gTTS

    stream = io.BytesIO()
    gTTS(text=piece, lang=lang, slow=False).write_to_fp(stream)
    return stream.getvalue()


def _gtts_bytes(text: str, lang: str) -> bytes:
    # gTTS makes one request per ~100 characters. Run the pieces in parallel
    # instead of one after another, then join the mp3 parts in order.
    pieces = textwrap.wrap(text, width=95, break_long_words=False) or [text]
    with ThreadPoolExecutor(max_workers=6) as pool:
        parts = list(pool.map(lambda piece: _gtts_piece(piece, lang), pieces))
    return b"".join(parts)


def synthesize_speech(text: str, language: str = "en") -> bytes:
    lang = tts_lang_code(language)
    spoken = prepare_speech_text(text, lang)
    if not spoken:
        spoken = {
            "te": "సలహా సిద్ధంగా ఉంది.",
            "hi": "सलाह तैयार है।",
        }.get(lang, "Advice is ready.")

    started = time.time()
    try:
        voice = EDGE_VOICES.get(lang, EDGE_VOICES["en"])
        data = _edge_tts_bytes(spoken, voice, SPEECH_RATES.get(lang, "+0%"))
        print(f"[tts] edge-tts {voice} {len(spoken)} chars in {time.time() - started:.1f}s")
        return data
    except Exception as exc:  # edge-tts missing or offline: fall back to gTTS
        print(f"[tts] edge-tts FAILED ({exc!r}); falling back to gTTS")
        data = _gtts_bytes(spoken, lang)
        print(f"[tts] gTTS fallback {len(spoken)} chars in {time.time() - started:.1f}s")
        return data