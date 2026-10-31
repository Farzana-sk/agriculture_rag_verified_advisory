"""Find the best spelling/voice for a word the Telugu voice mispronounces.

Run from the project root:   python src/tts_lab.py
It writes short mp3 files into the folder  tts_lab/  . Play them and note the
file number that sounds right. Change WORDS below to test other words.
"""
import asyncio
from pathlib import Path

import edge_tts

VOICES = {"shruti": "te-IN-ShrutiNeural", "mohan": "te-IN-MohanNeural"}
RATE = "-15%"

# Sentence with the word under test inside it; {w} is replaced by each spelling.
SENTENCE = "ఖరీఫ్‌లో హెక్టారుకు పద్దెనిమిది నుండి {w} క్వింటాళ్లు."
SPELLINGS = ["ఇరవై", "ఇరువై", "ఇరవయి", "ఇరవ్వై", "20"]


async def make(text: str, voice: str, path: Path) -> None:
    audio = bytearray()
    async for chunk in edge_tts.Communicate(text, voice, rate=RATE).stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    path.write_bytes(bytes(audio))


async def main() -> None:
    out = Path("tts_lab")
    out.mkdir(exist_ok=True)
    jobs, index = [], 0
    for voice_name, voice in VOICES.items():
        for spelling in SPELLINGS:
            index += 1
            path = out / f"{index:02d}_{voice_name}.mp3"
            print(f"{path.name}: voice={voice_name}  spelling={spelling}")
            jobs.append(make(SENTENCE.format(w=spelling), voice, path))
    await asyncio.gather(*jobs)
    print("\nDone. Play the files in the tts_lab folder and tell Claude the best number.")


if __name__ == "__main__":
    asyncio.run(main())
