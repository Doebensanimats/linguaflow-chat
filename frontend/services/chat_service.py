from services.aws_service import translate_text, text_to_speech


def process_message(text: str, src_lang: str, tgt_lang: str, voice: str):
    """
    Core chat pipeline: text → translate → speech
    Returns (translated_text, audio_bytes_or_None)
    """
    if not text or not text.strip():
        return "", None

    translated = translate_text(text, src_lang, tgt_lang)
    audio      = text_to_speech(translated, voice)

    return translated, audio
