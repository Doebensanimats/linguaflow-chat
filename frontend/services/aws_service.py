import boto3
import os
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

translate_client = boto3.client("translate", region_name=AWS_REGION)
polly_client     = boto3.client("polly",     region_name=AWS_REGION)

# Neural-capable voices — falls back to standard if neural unavailable
NEURAL_VOICES = {"Joanna", "Lupe", "Lea", "Vicki", "Camila"}


def translate_text(text: str, source: str, target: str) -> str:
    """Translate text using AWS Translate. Raises on failure."""
    if not text or not text.strip():
        return ""
    response = translate_client.translate_text(
        Text=text,
        SourceLanguageCode=source,
        TargetLanguageCode=target,
    )
    return response["TranslatedText"]


def translate_chunks(text: str, source: str, target: str, chunk_size: int = 4000) -> str:
    """Translate large text in chunks (for documents)."""
    if not text.strip():
        return ""
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    results = []
    for chunk in chunks:
        if chunk.strip():
            results.append(translate_text(chunk, source, target))
    return "\n".join(results)


def text_to_speech(text: str, voice: str, timeout: int = 8) -> bytes | None:
    """Synthesize speech with Polly. Returns MP3 bytes or None on failure."""
    if not text or not text.strip():
        return None
    try:
        engine = "neural" if voice in NEURAL_VOICES else "standard"
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(
                polly_client.synthesize_speech,
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice,
                Engine=engine,
                SampleRate="22050",
            )
            return future.result(timeout=timeout)["AudioStream"].read()
    except Exception as e:
        print(f"[Polly] TTS failed for voice={voice}: {e}")
        return None
