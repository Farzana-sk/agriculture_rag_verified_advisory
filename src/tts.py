import asyncio
import io
import textwrap
from concurrent.futures import ThreadPoolExecutor

try:
    from .language import prepare_speech_text, tts_lang_code
except ImportError:  # pragma: no cover - script execution support
    from language import prepare_speech_text, tts_lang_code

# Microsoft neural voices (edge-tts): one streaming request, much faster than gTTS.
EDGE_VOICES = {
    "en": "en-IN-NeerjaNeural",
    "te": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
}
SPEECH_RATE = "+10%"  # raise to "+20%" for faster speech


def _edge_tts_bytes(text: str, voice: str) -> bytes:
    import edge_tts

    async def run() -> bytes:
        audio = bytearray()
        communicate = edge_tts.Communicate(text, voice, rate=SPEECH_RATE)
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

    try:
        return _edge_tts_bytes(spoken, EDGE_VOICES.get(lang, EDGE_VOICES["en"]))
    except Exception as exc:  # edge-tts missing or offline: fall back to gTTS
        print(f"[tts] edge-tts failed ({exc}); falling back to gTTS")
        return _gtts_bytes(spoken, lang)