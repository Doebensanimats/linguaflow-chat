from fastapi import APIRouter, UploadFile
from services.aws_transcribe import transcribe_audio
from services.aws_polly import text_to_speech

router = APIRouter()

@router.post("/stt")
async def speech_to_text(file: UploadFile):
    audio = await file.read()
    text = transcribe_audio(audio)
    return {"text": text}

@router.post("/tts")
def text_to_audio(payload: dict):
    text = payload["text"]
    lang = payload["lang"]

    audio = text_to_speech(text, lang)
    return {"audio": audio}