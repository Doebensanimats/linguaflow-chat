from fastapi import APIRouter
from pydantic import BaseModel

from services.aws_translate import translate_text
from services.language_detect import detect_language

router = APIRouter()


# ── REQUEST MODEL ───────────────────────────────────────────
class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"   # auto-detect by default
    target: str = "en"


# ── TRANSLATION ENDPOINT ────────────────────────────────────
@router.post("/")
def translate(req: TranslateRequest):
    text = req.text.strip()

    if not text:
        return {
            "detected_language": None,
            "translated": ""
        }

    # ── AUTO DETECT LANGUAGE ────────────────────────────────
    detected_lang = (
        detect_language(text)
        if req.source == "auto"
        else req.source
    )

    # ── TRANSLATE ───────────────────────────────────────────
    translated_text = translate_text(
        text=text,
        source_lang=detected_lang,
        target_lang=req.target
    )

    return {
        "detected_language": detected_lang,
        "translated": translated_text
    }