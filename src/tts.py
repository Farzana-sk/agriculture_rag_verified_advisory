import io
import asyncio
import edge_tts
from language import prepare_speech_text, tts_lang_code

def synthesize_speech(text: str, language: str = "en") -> bytes:
    lang = tts_lang_code(language)
    spoken = prepare_speech_text(text, lang)
    
    if not spoken:
        spoken = {
            "te": "సలహా సిద్ధంగా ఉంది.",
            "hi": "सलाह तैयार है।",
        }.get(lang, "Advice is ready.")
    
    # Assign clear female neural voices based on language
    voice = "en-US-AriaNeural"
    if lang == "te":
        voice = "te-IN-ShrutiNeural"  # Clear Telugu Female Voice
    elif lang == "hi":
        voice = "hi-IN-SwaraNeural"   # Clear Hindi Female Voice

    async def get_audio():
        communicate = edge_tts.Communicate(spoken, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    # Run the async generation and return the audio bytes
    return asyncio.run(get_audio())