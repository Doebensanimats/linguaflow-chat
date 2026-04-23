import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

FIREBASE_KEY_PATH = os.path.join(
    BASE_DIR,
    "config",
    "firebase_key.json"
)