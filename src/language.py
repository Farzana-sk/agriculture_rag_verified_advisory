import re
import unicodedata

from groq import Groq

try:
    from .config import GROQ_API_KEY, LLM_MODEL, require_groq_key
except ImportError:  # pragma: no cover - script execution support
    from config import GROQ_API_KEY, LLM_MODEL, require_groq_key


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



def normalize_text(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKC", str(text))
    normalized = normalized.replace("\u00a0", " ").replace("\u200b", "")
    normalized = re.sub(r"[\u2000-\u200f\u202f\u205f\u3000]", " ", normalized)
    return normalized


def fold_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9\s]", " ", ascii_text.lower())


def looks_romanized_telugu(text: str) -> bool:
    # Word-level matching. The old substring check matched "vari" inside the
    # English word "varieties", so English questions were treated as Telugu.
    folded = fold_text(text)
    tokens = folded.split()
    strong_parts = (
        "rakalu", "rakaalu", "pratti", "prathi", "panta", "aakulu", "akulu",
        "emiti", "cheyyali", "cheyali", "paddi", "varirak",
    )
    if any(part in folded for part in strong_parts):
        return True
    return any(token in {"vari", "vaari"} for token in tokens)


def detect_language(text: str, whisper_language: str | None = None) -> str:
    text = text or ""
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


# English words that also appear in TELUGU_GLOSSARY; they do not prove the
# question is romanized Telugu.
_ENGLISH_SAFE = {
    "rice", "paddy", "tomato", "cotton", "yellow", "yello", "colour",
    "fungicide", "pesticide", "pesticides", "bollworm", "whitefly",
    "aphids", "urea", "doses",
}


def has_romanized_telugu_words(text: str) -> bool:
    tokens = fold_text(text).split()
    return any(t in TELUGU_GLOSSARY and t not in _ENGLISH_SAFE for t in tokens)


def is_plain_english(text: str) -> bool:
    text = text or ""
    return (
        text.isascii()
        and not looks_romanized_telugu(text)
        and not has_romanized_telugu_words(text)
    )


def rewrite_to_english(question: str) -> str:
    question = question or ""
    # SPEED: plain English needs no LLM rewrite (saves one Groq call).
    if is_plain_english(question):
        return question.strip()
    heuristic = heuristic_english_query(question)
    folded = fold_text(question)
    if heuristic in {"recommended paddy varieties", "recommended cotton varieties"}:
        return heuristic
    if not GROQ_API_KEY:
        return heuristic or question

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


# SPEED: False = take the first sentences of the answer (no extra LLM call).
# Set True to restore the older LLM-written 2-sentence spoken summary.
USE_LLM_SPOKEN_SUMMARY = False
_TELUGU_SPEECH_UNAVAILABLE = "క్షమించండి, ఈ సమాధానాన్ని తెలుగులో వినిపించలేకపోతున్నాను. తెరపై చదవండి."
_TELUGU_UNVERIFIED_PREFIX = "ఖచ్చితమైన తెలుగు అనువాదం సాధ్యం కాలేదు."


def _needs_telugu_translation(text: str) -> bool:
    has_telugu = any("\u0c00" <= ch <= "\u0c7f" for ch in text)
    return text.startswith(_TELUGU_UNVERIFIED_PREFIX) or (
        not has_telugu and bool(re.search(r"[A-Za-z]", text))
    )


def first_sentences(text: str, count: int = 3, max_chars: int = 500) -> str:
    parts = re.split(r"(?<=[.!?\u0964])\s+", (text or "").strip())
    return " ".join(parts[:count])[:max_chars]


def spoken_summary(text: str, language: str = "en") -> str:
    """Short, TTS-friendly line in the farmer's language."""
    text = text or ""
    if not text.strip():
        return text
    if language == "te" and _needs_telugu_translation(text):
        return _TELUGU_SPEECH_UNAVAILABLE
    if not USE_LLM_SPOKEN_SUMMARY or not GROQ_API_KEY:
        # Read the FULL answer (sentence cutting broke on '1.' and 'G. hirsutum').
        return prepare_speech_text(text, language)
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



_TE_ONES = ["సున్నా", "ఒకటి", "రెండు", "మూడు", "నాలుగు", "ఐదు", "ఆరు", "ఏడు", "ఎనిమిది", "తొమ్మిది",
            "పది", "పదకొండు", "పన్నెండు", "పదమూడు", "పద్నాలుగు", "పదిహేను", "పదహారు", "పదిహేడు",
            "పద్దెనిమిది", "పంతొమ్మిది"]
_TE_TENS = {2: "ఇరవై", 3: "ముప్పై", 4: "నలభై", 5: "యాభై", 6: "అరవై", 7: "డెబ్బై", 8: "ఎనభై", 9: "తొంభై"}


def telugu_number_words(n: int) -> str:
    """Convert non-negative integers below one billion to spoken Telugu."""
    if not 0 <= n < 1_000_000_000:
        raise ValueError("Telugu number conversion supports values from 0 to 999999999.")
    if n < 20:
        return _TE_ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return _TE_TENS[tens] + (" " + _TE_ONES[ones] if ones else "")
    if n < 1000:
        hundreds, rest = divmod(n, 100)
        if hundreds == 1:
            return "వంద" if not rest else "నూట " + telugu_number_words(rest)
        return _TE_ONES[hundreds] + (" వందల " + telugu_number_words(rest) if rest else " వందలు")
    if n < 100_000:
        thousands, rest = divmod(n, 1000)
        if thousands == 1:
            return "వెయ్యి" + (" " + telugu_number_words(rest) if rest else "")
        head = telugu_number_words(thousands)
        return head + (" వేల " + telugu_number_words(rest) if rest else " వేలు")

    if n < 10_000_000:
        lakhs, rest = divmod(n, 100_000)
        head = "ఒక" if lakhs == 1 else telugu_number_words(lakhs)
        suffix = (" లక్ష" if lakhs == 1 else " లక్షల") if rest else (
            " లక్ష" if lakhs == 1 else " లక్షలు"
        )
        return head + suffix + (" " + telugu_number_words(rest) if rest else "")

    crores, rest = divmod(n, 10_000_000)
    head = "ఒక" if crores == 1 else telugu_number_words(crores)
    suffix = (" కోటి" if crores == 1 else " కోట్ల") if rest else (
        " కోటి" if crores == 1 else " కోట్లు"
    )
    return head + suffix + (" " + telugu_number_words(rest) if rest else "")


def telugu_numbers_to_words(text: str) -> str:
    def convert(match):
        value = match.group(0)
        if re.fullmatch(_TELUGU_NUMBER_CODES, value):
            return value
        whole, _, frac = value.partition(".")
        digits = whole.replace(",", "")
        if len(digits) > 9:
            return value
        words = telugu_number_words(int(digits))
        if frac:
            words += " పాయింట్ " + " ".join(_TE_ONES[int(d)] for d in frac)
        return words

    _TELUGU_NUMBER_CODES = (
        r"\b(?:[A-Z]{2,}(?:\s+[A-Z]{2,}){0,2}|[A-Z]{2,}\s+[A-Z][a-z]+)"
        r"[ -]\d[\d,]*(?:-\d+)?\b"
    )
    number_pattern = (
        _TELUGU_NUMBER_CODES
        + r"|(?:\d{1,3}(?:,\d{3})+|\d{1,3}(?:,\d{2})*,\d{3})(?:\.\d+)?"
        r"|\d+(?:\.\d+)?"
    )
    return re.sub(number_pattern, convert, _to_ascii_digits(text), flags=re.ASCII)


def prepare_speech_text(text: str, language: str = "en") -> str:
    text = normalize_text(text)
    if language == "te" and text.strip() and _needs_telugu_translation(text):
        return _TELUGU_SPEECH_UNAVAILABLE
    # Text inside ( ) or [ ] becomes its own spoken segment, marked with "|".
    # tts.py pauses at each "|", so bracket info is read AFTER the sentence ends.
    text = re.sub(
        r"\s*[(\[]([^()\[\]]*)[)\]]",
        lambda m: f" | {m.group(1).strip()} | " if m.group(1).strip() else " ",
        text,
    )
    if language == "te":
        text = re.sub(r"(?m)^\s*[-*•]\s+", "", text)
        text = re.sub(r"(?<=[.!?])\s*\n\s*", " ", text)
        text = re.sub(r"\s*\n\s*", ". ", text)
    if language in ("te", "hi"):
        joiner = " \u0c28\u0c41\u0c02\u0c21\u0c3f " if language == "te" else " \u0938\u0947 "
        text = re.sub(r"(?<=\d)\s*[-\u2010-\u2015]\s*(?=\d)", joiner, text)
        if language == "te":
            unit_replacements = (
                (r"\bkg\s*/\s*ha\b", "కిలోలు ప్రతి హెక్టారుకు"),
                (r"\bq\s*/\s*ha\b", "క్వింటాళ్లు ప్రతి హెక్టారుకు"),
                (r"\bt\s*/\s*ha\b", "టన్నులు ప్రతి హెక్టారుకు"),
                (r"\bg\s*/\s*ha\b", "గ్రాములు ప్రతి హెక్టారుకు"),
                (r"\bkg\s*/\s*acre\b", "కిలోలు ఎకరానికి"),
                (r"\bq\s*/\s*acre\b", "క్వింటాళ్లు ఎకరానికి"),
                (r"\bkg\b", "కిలోలు"),
                (r"\bcm\b", "సెంటీమీటర్లు"),
                (r"\bha\b", "హెక్టారు"),
                (r"\bacre\b", "ఎకరం"),
            )
            for pattern, replacement in unit_replacements:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        text = text.replace("/", " ").replace("%", " శాతం " if language == "te" else " प्रतिशत ")
        if language == "te":
            text = telugu_numbers_to_words(text)
    if language == "en":
        # English TTS can read numbers, so keep them and make symbols speakable.
        text = re.sub(r"[\u2010-\u2015\u2212]", "-", text)
        text = text.replace("\u00d7", " cross ").replace("%", " percent ").replace("/", " per ")
        text = re.sub(r"(?<=\d)\s*-\s*(?=\d)", " to ", text)
        text = text.replace("-", " ")
    cleaned = re.sub(r"[*_`#>()\[\]{}]+", " ", text or "")
    letters = []
    for ch in cleaned:
        # Keep letters (L*) AND combining marks (M*). Telugu/Hindi vowel signs
        # such as ా ి ు ్ are category M*, and isalpha() is False for them.
        category = unicodedata.category(ch)
        keep_digit = ch.isdigit()
        if category[0] in ("L", "M") or keep_digit or ch.isspace() or ch in " .,;:'-|\u0964":
            letters.append(ch)
    cleaned = re.sub(r"\s+", " ", "".join(letters)).strip(" .-")
    if language == "en":
        cleaned = "".join(ch if ord(ch) < 128 else " " for ch in cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .-")
        if len(cleaned.split()) < 6:
            return "Here are the recommended crop varieties from the official package of practices."
    elif language == "hi" and len(cleaned) < 12:
        return "आधिकारिक दस्तावेज के अनुसार अनुशंसित फसल किस्में ये हैं।"
    return cleaned[:1500]


# ---------------------------------------------------------------------------
# Safe translation: units are expanded before translating, key terms are fixed
# by a glossary, and the result is CHECKED (numbers + units) before release.
# ---------------------------------------------------------------------------
_UNIT_EXPANSIONS = [
    (r"\bq\s*/\s*ha\b", "quintals per hectare"),
    (r"\bt\s*/\s*ha\b", "tonnes per hectare"),
    (r"\bkg\s*/\s*ha\b", "kilograms per hectare"),
    (r"\bg\s*/\s*ha\b", "grams per hectare"),
    (r"\bq\s*/\s*acre\b", "quintals per acre"),
    (r"\bcm\b", "centimetres"),
    (r"\bkg\b", "kilograms"),
]

_GLOSSARY = {
    "te": (
        "Kharif = ఖరీఫ్; Rabi = రబీ; paddy = వరి; cotton = పత్తి; groundnut = వేరుశనగ; "
        "chilli = మిరప; tomato = టమాటా; brinjal = వంకాయ; quintals = క్వింటాళ్లు; "
        "kilograms = కిలోలు; grams = గ్రాములు; tonnes = టన్నులు; hectare = హెక్టారు; "
        "days = రోజులు; centimetres = సెంటీమీటర్లు; seed rate = విత్తన మోతాదు; "
        "spacing = మొక్కల మధ్య దూరం; crop duration = పంట కాలం; variety = రకం; yield = దిగుబడి"
    ),
    "hi": (
        "Kharif = खरीफ; Rabi = रबी; paddy = धान; cotton = कपास; groundnut = मूंगफली; "
        "chilli = मिर्च; tomato = टमाटर; brinjal = बैंगन; quintals = क्विंटल; "
        "kilograms = किलोग्राम; grams = ग्राम; tonnes = टन; hectare = हेक्टेयर; "
        "days = दिन; centimetres = सेंटीमीटर; seed rate = बीज दर; "
        "spacing = पौधों के बीच दूरी; crop duration = फसल अवधि; variety = किस्म; yield = उपज"
    ),
}

# Common wrong spellings the model produces -> correct form.
_SPELLING_FIXES = {
    "te": {"రాబీ": "రబీ", "రబి": "రబీ", "రాబి": "రబీ", "ఖరిఫ్": "ఖరీఫ్", "కరీఫ్": "ఖరీఫ్"},
    "hi": {"रबि": "रबी", "खरिफ": "खरीफ"},
}

_UNIT_WORDS = {  # english stem -> expected word stem in each language
    "te": {"quintal": "క్వింటా", "kilogram": "కిలో"},
    "hi": {"quintal": "क्विंटल", "kilogram": "किलो"},
}


def expand_units(text: str) -> str:
    for pattern, replacement in _UNIT_EXPANSIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _to_ascii_digits(text: str) -> str:
    return "".join(str(unicodedata.digit(ch)) if ch.isdigit() else ch for ch in text)


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", _to_ascii_digits(text)))


def check_translation(english: str, translated: str, language: str) -> list[str]:
    """Return a list of problems; an empty list means the translation is safe."""
    problems = []
    missing = sorted(_numbers(english) - _numbers(translated), key=float)
    if missing:
        problems.append("numbers missing or changed: " + ", ".join(missing))
    low = english.lower()
    words = _UNIT_WORDS[language]
    en_has = {
        "quintal": "quintal" in low,
        "kilogram": bool(re.search(r"kilogram|\bkg\b|\bkilo\b", low)),
    }
    for stem, expected in words.items():
        in_translation = expected in translated
        if en_has[stem] and not in_translation:
            problems.append(f"unit '{stem}' not translated correctly")
        if in_translation and not en_has[stem]:
            problems.append(f"unit '{stem}' appears but is not in the English answer")
    return problems


def _apply_spelling_fixes(text: str, language: str) -> str:
    for wrong, right in _SPELLING_FIXES[language].items():
        text = text.replace(wrong, right)
    return text


def _call_translate(client, english: str, language: str, feedback: str = "") -> str:
    lang_name = "Telugu" if language == "te" else "Hindi"
    if language == "te":
        style = """Translate into natural, conversational Andhra Telugu, as an agriculture officer would explain it clearly to a farmer.
Do not translate word for word or use stiff, formal constructions. Prefer short, direct, familiar Telugu sentences.
Write entirely in Telugu script except for crop and variety names or codes. Keep names like Sona Mahsuri, Samba Mahsuri, LHDP Cotton-1, TCG 1704 and ICGV 00350 exactly as written.
Keep every number and unit exactly as written; do not add, remove, reorder, or alter any recommendation or fact.
Keep each recommendation on its own line. When there are multiple recommendations, format each as a dash bullet and bold only its crop or variety name using **name**."""
    else:
        style = f"""Translate this agricultural advice into clear, natural, simple spoken {lang_name} for a farmer in Andhra Pradesh.
Write every sentence in {lang_name} script. Do not leave English phrases or sentences untranslated.
Keep variety names like Sona Mahsuri, Samba Mahsuri, LHDP Cotton-1 as they are.
Keep every number as digits 0-9 exactly as written. Never change, add or drop a number or a unit."""
    prompt = f"""{style}
Use these exact terms: {_GLOSSARY[language]}.
{feedback}Return only the {lang_name} translation.

{english}"""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_completion_tokens=700,
        reasoning_effort="low",
        include_reasoning=False,
    )
    translated = (response.choices[0].message.content or "").strip()
    return _apply_spelling_fixes(translated, language)


def _has_script(text: str, language: str) -> bool:
    lo, hi = (0x0C00, 0x0C7F) if language == "te" else (0x0900, 0x097F)
    return any(lo <= ord(ch) <= hi for ch in text)


_UNVERIFIED_NOTICE = {
    "te": _TELUGU_UNVERIFIED_PREFIX + " ఇంగ్లీష్ సమాధానం: ",
    "hi": "सटीक हिंदी अनुवाद संभव नहीं हुआ। अंग्रेज़ी उत्तर: ",
}


def translate_answer(text: str, language: str) -> str:
    text = normalize_text(text or "")
    if language not in {"te", "hi"} or not text.strip():
        return text
    if not GROQ_API_KEY:
        return text
    english = expand_units(text)
    client = Groq(api_key=require_groq_key(), timeout=25.0)

    translated = _call_translate(client, english, language)
    problems = [] if _has_script(translated, language) else ["answer is not in the target script"]
    problems += check_translation(english, translated, language) if translated else ["empty translation"]

    for _ in range(2):  # up to two corrective retries
        if not problems:
            return translated
        feedback = "Fix these problems from the previous attempt: " + "; ".join(problems) + ".\n"
        translated = _call_translate(client, english, language, feedback)
        problems = [] if _has_script(translated, language) else ["answer is not in the target script"]
        problems += check_translation(english, translated, language) if translated else ["empty translation"]

    if not problems:
        return translated
    print(f"[translate] unsafe translation withheld: {problems}")
    return _UNVERIFIED_NOTICE[language] + english