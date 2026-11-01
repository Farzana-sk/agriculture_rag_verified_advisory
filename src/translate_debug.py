"""Shows WHY a Telugu translation is rejected. Run:  python src\\translate_debug.py
Writes translate_debug.txt in the project folder (UTF-8). Send me that file."""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from groq import Groq

from config import LLM_MODEL, require_groq_key
from language import (
    _call_translate,
    _has_script,
    check_translation,
    expand_units,
    normalize_text,
)

SAMPLES = [
    "Here are the paddy varieties listed in the provided documents:",
    "1. **Prabhat (MTU 3626)** – high-yielding, blast-tolerant, coarse grain, suitable for the Godavari Delta.",
    "2. **Pushyami (MTU 1075)** – non-lodging, tolerant to BPH, released by CVRC in 2008, suitable for Andhra Pradesh, Tamil Nadu, Gujarat and Maharashtra.",
]

out = Path(__file__).resolve().parent.parent / "translate_debug.txt"
lines = [f"model: {LLM_MODEL}"]
try:
    client = Groq(api_key=require_groq_key(), timeout=45.0)
    for sample in SAMPLES:
        english = expand_units(normalize_text(sample))
        lines.append("\n=== ENGLISH ===\n" + english)
        try:
            translated = _call_translate(client, english, "te")
            lines.append("--- RAW TELUGU ---\n" + translated)
            lines.append(f"has Telugu script: {_has_script(translated, 'te')}")
            lines.append(f"problems: {check_translation(english, translated, 'te')}")
        except Exception:
            lines.append("API/CODE ERROR:\n" + traceback.format_exc())
except Exception:
    lines.append("SETUP ERROR:\n" + traceback.format_exc())

out.write_text("\n".join(lines), encoding="utf-8")
print(f"Done. Open or send this file: {out}")
