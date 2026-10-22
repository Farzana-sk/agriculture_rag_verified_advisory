import re
import unicodedata

from groq import Groq

from config import LLM_MODEL, require_groq_key


TELUGU_GLOSSARY = {
    # ---------------- CROPS ----------------
    "pratti": "cotton",
    "prathi": "cotton",
    "pratthi": "cotton",
    "parthi": "cotton",
    "pathi": "cotton",
    "patti": "cotton",
    "patthi": "cotton",
    "pratti panta": "cotton crop",
    "patti panta": "cotton crop",
    "vari": "paddy",
    "vaari": "paddy",
    "vaaru": "paddy",
    "vari panta": "paddy crop",
    "vaaripanta": "paddy crop",
    "paddi": "paddy",
    "vys": "paddy",
    "rice": "paddy",
    "paddy": "paddy",
    "mirapa": "chilli",
    "mirapalu": "chillies",
    "mirchi": "chilli",
    "mokkajonna": "maize",
    "jonna": "sorghum",
    "pesara": "green gram",
    "pesalu": "green gram",
    "minumulu": "black gram",
    "senaga": "chickpea",
    "verusanaga": "groundnut",
    "vankaya": "brinjal",
    "tomato": "tomato",
    "tamata": "tomato",
    "arati": "banana",
    "cheruku": "sugarcane",
    "pasupu": "turmeric",
    "mamidi": "mango",

    # ---------------- QUESTIONS ----------------
    "emiti": "what",
    "emitii": "what",
    "enti": "what",
    "enduku": "why",
    "ela": "how",
    "elaa": "how",
    "eppudu": "when",
    "ekkada": "where",
    "entha": "how much",
    "enni": "how many",
    "edi": "which",
    "yevi": "which",
    "yevi cheppandi": "which ones",
    "cheppandi": "please tell",
    "cheppu": "tell me",
    "teliyali": "want to know",
    "kavali": "need",
    "kaavali": "need",
    "cheyyali": "what should be done",
    "cheyali": "what should be done",
    "em cheyyali": "what should be done",
    "emi cheyyali": "what should be done",
    "em cheyali": "what should be done",
    "ela cheyyali": "how to do",
    "ela veyali": "how to apply",
    "eppudu veyali": "when to apply",

    # ---------------- VARIETIES / SEEDS ----------------
    "rakalu": "varieties",
    "rakaalu": "varieties",
    "rakaluu": "varieties",
    "rakaluulu": "varieties",
    "rakalu enti": "varieties",
    "vithanalu": "seeds",
    "vittanalu": "seeds",
    "ginjalu": "seeds",
    "manchi vittanalu": "good quality seeds",
    "yem rakam": "which variety",
    "ye rakam": "which variety",
    "panta rakam": "crop variety",

    # ---------------- PLANT PARTS ----------------
    "aaku": "leaf",
    "aakulu": "leaves",
    "akulu": "leaves",
    "aakuluu": "leaves",
    "aku": "leaf",
    "aku lu": "leaves",
    "verlu": "roots",
    "veru": "root",
    "kandam": "stem",
    "kommalu": "branches",
    "puvvu": "flower",
    "puvvulu": "flowers",
    "kaayalu": "fruits",
    "pandu": "fruit",
    "ginja": "seed",

    # ---------------- PLANT SYMPTOMS ----------------
    "pasupu": "yellow",
    "pasupu ga": "yellow",
    "pasupu rangulo": "yellow",
    "pachaga": "green",
    "nalla": "black",
    "tellaga": "white",
    "erra": "red",
    "aakulu pasupu": "yellow leaves",
    "aakulu endipothunnayi": "leaves are drying",
    "endipothundi": "is drying",
    "endipothunnayi": "are drying",
    "vaadipothundi": "is wilting",
    "vaadipothunnayi": "are wilting",
    "peragatledu": "not growing",
    "edugudala ledu": "poor plant growth",
    "mokkalau chanipothunnayi": "plants are dying",
    "aakulu raaluthunnayi": "leaves are falling",
    "machalu": "spots",
    "macha": "spot",
    "madata paduthunnayi": "leaves are curling",
    "purugulu": "insects",
    "purugu": "pest",
    "tegulu": "disease",
    "rogaalu": "diseases",
    "rogalu": "diseases",

    # ---------------- PESTS / DISEASES ----------------
    "purugu pattindi": "pest infestation",
    "purugulu pattayi": "pest infestation",
    "purugu undi": "pests are present",
    "tegulu vachindi": "crop disease",
    "rogaalu vachayi": "crop diseases",
    "cheema": "ant",
    "cheemalu": "ants",
    "tellapurugu": "white insect pest",
    "aaku purugu": "leaf-eating caterpillar",
    "bollworm": "bollworm",
    "whitefly": "whitefly",
    "aphids": "aphids",
    "doma": "hopper",
    "domalu": "hoppers",

    # ---------------- FERTILIZERS / PESTICIDES ----------------
    "mandu": "pesticide",
    "mandu": "pesticide",
    "mandulu": "pesticides",
    "purugu mandu": "insecticide",
    "tegulu mandu": "disease control treatment",
    "fungicide": "fungicide",
    "pesticide": "pesticide",
    "pesticides": "pesticides",
    "eruvu": "fertilizer",
    "eruvulu": "fertilizers",
    "sendreeya eruvu": "organic fertilizer",
    "rasayana eruvu": "chemical fertilizer",
    "kompost": "compost",
    "vermi compost": "vermicompost",
    "urea": "urea fertilizer",
    "poshakalu": "nutrients",
    "saram": "nutrient content",
    "doses": "application doses",

    # ---------------- FARMING ACTIVITIES ----------------
    "saagu": "cultivation",
    "saagu cheyyali": "cultivate",
    "vyavasayam": "agriculture",
    "panta": "crop",
    "pantalu": "crops",
    "natu": "transplant",
    "natlu": "transplanting",
    "vithadam": "sowing",
    "vithali": "should sow",
    "veyali": "should apply or sow",
    "challadam": "spraying",
    "kottali": "should spray",
    "pichikari": "spraying",
    "koyadam": "harvesting",
    "panta koyali": "harvest the crop",
    "kalupu": "weed",
    "kalupu mokkalu": "weeds",
    "kalupu tiyali": "weed removal",

    # ---------------- WATER / WEATHER ----------------
    "neeru": "water",
    "neellu": "water",
    "neeti": "water",
    "neellu poyali": "irrigation",
    "neeru pettali": "irrigate",
    "neeru saripovatledu": "insufficient water",
    "varsham": "rain",
    "varshalu": "rainfall",
    "endalu": "hot weather",
    "vedi": "heat",
    "challaga": "cold",
    "chali": "cold weather",
    "karuvu": "drought",
    "munigipoyindi": "waterlogging",
    "gaali": "wind",

    # ---------------- YIELD / HARVEST ----------------
    "digubadi": "crop yield",
    "digubadi takkuva": "low crop yield",
    "digubadi perigali": "increase crop yield",
    "panta nashtam": "crop loss",
    "nashtam": "damage",
    "labham": "profit",
    "dhara": "price",
    "market dhara": "market price",
    "ammandi": "sell",
    "pantanu ammadam": "selling the crop",

    # ---------------- COMMON ENGLISH WORDS ----------------
    "yellow": "yellow",
    "yello": "yellow",
    "kalarlo": "colour",
    "kalar": "colour",
    "rangu": "colour",
    "rangulu": "colours",
    "colour": "colour",
    "cotton": "cotton",
    "rice": "paddy",
    "paddy": "paddy",
}



def fold_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9\s]", " ", ascii_text.lower())


def looks_romanized_telugu(text: str) -> bool:
    folded = fold_text(text)
    clues = (
        "panta",
        "pratti",
        "prathi",
        "paddi",
        "vari",
        "rakalu",
        "emiti",
        "aakulu",
        "akulu",
        "cheyyali",
        "cheyali",
        "veste",
        "kalar",
    )
    return sum(clue in folded for clue in clues) >= 1 and (
        "vari" in folded or "pratti" in folded or "panta" in folded or "rakalu" in folded
    )


def detect_language(text: str, whisper_language: str | None = None) -> str:
    if any("\u0c00" <= ch <= "\u0c7f" for ch in text):
        return "te"
    if any("\u0900" <= ch <= "\u097f" for ch in text):
        return "hi"
    if looks_romanized_telugu(text):
        return "te"
    if whisper_language:
        code = whisper_language.lower()[:2]
        if code in {"en", "hi", "te"}:
            return code
    try:
        from langdetect import detect

        code = detect(text)
        if code in {"en", "hi", "te"}:
            return code
    except Exception:
        pass
    return "en"


def tts_lang_code(language: str) -> str:
    return {"en": "en", "hi": "hi", "te": "te"}.get(language, "en")


def heuristic_english_query(text: str) -> str:
    folded = fold_text(text)
    if "vari" in folded and "rakalu" in folded:
        return "recommended paddy varieties"
    if any(word in folded for word in ("pratti", "prathi", "cotton")) and "rakalu" in folded:
        return "recommended cotton varieties"
    if "paddi" in folded and any(token in folded for token in ("aakulu", "akulu", "yellow", "ello", "kalar")):
        folded = folded.replace("paddi", "cotton")
    parts = [TELUGU_GLOSSARY.get(word, word) for word in folded.split() if word]
    return " ".join(parts).strip()


def rewrite_to_english(question: str) -> str:
    heuristic = heuristic_english_query(question)
    folded = fold_text(question)
    if heuristic in {"recommended paddy varieties", "recommended cotton varieties"}:
        return heuristic

    client = Groq(api_key=require_groq_key(), timeout=20.0)
    prompt = f"""Rewrite this farmer question as one short English agriculture search query.
Telugu glossary (romanized):
- vari = paddy/rice
- rakalu / rakaalu = VARIETIES (not colours)
- rangu / rangulu = colours
- pratti / prathi panta = cotton
- aakulu = leaves
- emiti / enti = what are
Return only the English query.

Original: {question}
Hint: {heuristic}
English query:"""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_completion_tokens=80,
        reasoning_effort="low",
        include_reasoning=False,
    )
    rewritten = (response.choices[0].message.content or "").strip().strip('"')
    if "color" in rewritten.lower() and "rakalu" in folded and "rangu" not in folded:
        return heuristic or "recommended paddy varieties"
    return rewritten or heuristic or question


def spoken_summary(text: str, language: str = "en") -> str:
    """Short, TTS-friendly line in the farmer's language."""
    if not text.strip():
        return text
    if language == "te":
        instruction = (
            "Rewrite this as 2 short Telugu sentences for a farmer. "
            "Use only Telugu script. Keep variety names. No digits. "
            "No English sentences. Return only those 2 sentences.\n\n"
        )
    elif language == "hi":
        instruction = (
            "Rewrite this as 2 short Hindi sentences for a farmer. "
            "Use only Hindi script. Keep variety names. No digits. "
            "Return only those 2 sentences.\n\n"
        )
    else:
        instruction = (
            "Rewrite this as 2 short English sentences for a farmer. "
            "No digits or codes. Return only those 2 sentences.\n\n"
        )
    client = Groq(api_key=require_groq_key(), timeout=20.0)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": instruction + text[:1500]}],
        temperature=0,
        max_completion_tokens=180,
        reasoning_effort="low",
        include_reasoning=False,
    )
    summary = (response.choices[0].message.content or "").strip()
    return prepare_speech_text(summary or text, language)


def prepare_speech_text(text: str, language: str = "en") -> str:
    cleaned = re.sub(r"[*_`#>()\[\]{}]+", " ", text or "")
    letters = []
    for ch in cleaned:
        if ch.isdigit():
            continue
        if ch.isalpha() or ch.isspace() or ch in " .,;:'-":
            letters.append(ch)
    cleaned = re.sub(r"\s+", " ", "".join(letters)).strip(" .-")
    if language == "en":
        cleaned = "".join(ch if ord(ch) < 128 else " " for ch in cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .-")
        if len(cleaned.split()) < 6:
            return "Here are the recommended crop varieties from the official package of practices."
    elif language == "te" and len(cleaned) < 12:
        return "అధికారిక పత్రాల ప్రకారం సిఫారసు చేసిన పంట రకాలు ఇవి."
    elif language == "hi" and len(cleaned) < 12:
        return "आधिकारिक दस्तावेज के अनुसार अनुशंसित फसल किस्में ये हैं।"
    return cleaned[:900]


def translate_answer(text: str, language: str) -> str:
    if language not in {"te", "hi"} or not text.strip():
        return text
    lang_name = "Telugu" if language == "te" else "Hindi"
    client = Groq(api_key=require_groq_key(), timeout=25.0)
    prompt = f"""Translate this agricultural advice into simple spoken {lang_name} for a farmer in Andhra Pradesh.
Write the whole answer in {lang_name} script, not English.
Keep variety names like Sona Mahsuri, Samba Mahsuri, LHDP Cotton-1 as they are.
Do not use digits; write quantities in words if needed.
Return only the {lang_name} translation.

{text}"""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_completion_tokens=500,
        reasoning_effort="low",
        include_reasoning=False,
    )
    translated = (response.choices[0].message.content or "").strip()
    needs_script = (language == "te" and not any("\u0c00" <= ch <= "\u0c7f" for ch in translated)) or (
        language == "hi" and not any("\u0900" <= ch <= "\u097f" for ch in translated)
    )
    if needs_script:
        retry = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": f"ఈ వాక్యాలను తెలుగులోకి అనువదించు. ఆంగ్ల వాక్యాలు రాయవద్దు.\n\n{text}"
                    if language == "te"
                    else f"इस सलाह का हिंदी में अनुवाद करें। अंग्रेज़ी वाक्य न लिखें।\n\n{text}",
                }
            ],
            temperature=0,
            max_completion_tokens=500,
            reasoning_effort="low",
            include_reasoning=False,
        )
        translated = (retry.choices[0].message.content or translated).strip()
    return translated or text
