import uuid

# firebase_admin is optional — app works without it
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

_db = None


def init_firebase():
    """
    Initialise Firebase and return the Firestore client.
    Returns None if firebase_admin is not installed or key is missing.
    """
    global _db

    if not FIREBASE_AVAILABLE:
        return None

    if _db is not None:
        return _db

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        return _db
    except Exception as e:
        print(f"[Firebase] init failed: {e}")
        return None


def create_room() -> str:
    """Generate a short random room ID."""
    return str(uuid.uuid4())[:8]


def send_message(room_id: str, data: dict) -> bool:
    """Add a message to a room. Returns True on success."""
    if _db is None:
        return False
    try:
        _db.collection("rooms").document(room_id) \
           .collection("messages").add(data)
        return True
    except Exception as e:
        print(f"[Firebase] send_message failed: {e}")
        return False


def get_messages(room_id: str) -> list:
    """Fetch all messages for a room, ordered by time. Returns list."""
    if _db is None:
        return []
    try:
        docs = _db.collection("rooms").document(room_id) \
                  .collection("messages").order_by("time").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"[Firebase] get_messages failed: {e}")
        return []
