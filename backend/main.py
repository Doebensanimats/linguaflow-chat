import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from routes import chat, translate, voice, health

app = FastAPI(title="LinguaFlow API")

app.include_router(chat.router, prefix="/chat")
app.include_router(translate.router, prefix="/translate")
app.include_router(voice.router, prefix="/voice")
app.include_router(health.router)

@app.get("/")
def root():
    return {"status": "LinguaFlow backend running"}