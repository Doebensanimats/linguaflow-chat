from langdetect import detect, DetectorFactory

# makes results stable (important)
DetectorFactory.seed = 0


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"  # fallback language