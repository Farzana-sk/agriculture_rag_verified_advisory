"""Shows what language each PDF is in and whether it mentions harvest/paddy.
Run:  python src\\pdf_peek.py      (output is plain ASCII, safe to paste)"""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

pdf_dir = Path(__file__).resolve().parent.parent / "data" / "raw_pdfs"
KEYWORDS = {
    "harvest": r"harvest",
    "paddy": r"paddy|rice",
    "te_kota(harvest)": "కోత",
    "te_vari(paddy)": "వరి",
}

for pdf in sorted(pdf_dir.glob("*.pdf")):
    if "test_questions" in pdf.name.lower():
        continue
    try:
        reader = PdfReader(str(pdf))
        pages = len(reader.pages)
        text = "\n".join((reader.pages[i].extract_text() or "") for i in range(pages))
    except Exception as exc:
        print(f"{pdf.name}: could not read ({exc})")
        continue
    telugu = len(re.findall(r"[ఀ-౿]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    total = telugu + latin
    hits = {name: len(re.findall(pattern, text, flags=re.I)) for name, pattern in KEYWORDS.items()}
    share = f"{100 * telugu / total:.0f}%" if total else "n/a"
    print(f"{pdf.name}: pages={pages} chars={len(text)} telugu_share={share} {hits}")