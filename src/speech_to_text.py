import os
import sounddevice as sd
from scipy.io.wavfile import write
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=api_key)


def transcribe_voice_question():

    sample_rate = 16000
    duration = 5

    print("\nSpeak your agricultural question...")
    print("Recording started...")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    print("Recording finished.")

    audio_file = "farmer_question.wav"

    write(audio_file, sample_rate, audio)

    with open(audio_file, "rb") as file:

        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",
            response_format="text",
            temperature=0
        )

    query = transcription.strip()

    print("\n--- TRANSCRIBED QUESTION ---")
    print(query)

    return query