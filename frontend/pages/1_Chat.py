# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
import re
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime, timezone
import html
import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from services.api_client import translate
from config.settings import FIREBASE_KEY_PATH
from config.Languages import LANGUAGES


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="LinguaFlow Chat", layout="wide")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def strip_tags(val):
    """Remove any HTML tags accidentally stored in Firestore fields."""
    return re.sub(r'<[^>]+>', '', str(val or ""))


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = ""

if "source_lang" not in st.session_state:
    st.session_state.source_lang = "en"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "es"

if "messages_cache" not in st.session_state:
    st.session_state.messages_cache = []

if "last_timestamp" not in st.session_state:
    st.session_state.last_timestamp = None


# ─────────────────────────────────────────────
# FIREBASE INIT
# ─────────────────────────────────────────────
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = get_db()


# ─────────────────────────────────────────────
# ROOM
# ─────────────────────────────────────────────
room_id = st.query_params.get("room", None)

if not room_id:
    st.title("🌐 LinguaFlow Chat")
    if st.button("Create Room"):
        new_room = str(uuid.uuid4())[:6]
        st.query_params["room"] = new_room
        st.rerun()
    st.stop()


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────
st.title(f"💬 Room: {room_id}")

st.session_state.username = st.text_input(
    "Name", value=st.session_state.username
)

if not st.session_state.username:
    st.stop()


# ─────────────────────────────────────────────
# LANGUAGE SELECTOR
# ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    source_name = st.selectbox("From", list(LANGUAGES.keys()))
with col2:
    target_name = st.selectbox("To", list(LANGUAGES.keys()))

st.session_state.source_lang = LANGUAGES[source_name]
st.session_state.target_lang = LANGUAGES[target_name]


# ─────────────────────────────────────────────
# SEND MESSAGE
# ─────────────────────────────────────────────
def send_message(text: str):
    text = text.strip()
    if not text:
        return

    translated = translate(
        text,
        st.session_state.source_lang,
        st.session_state.target_lang
    )

    db.collection("rooms").document(room_id).collection("messages").add({
        "user": st.session_state.username,
        "text": text,
        "translated": translated,
        "timestamp": datetime.now(timezone.utc)
    })


# ─────────────────────────────────────────────
# FETCH MESSAGES (INCREMENTAL)
# ─────────────────────────────────────────────
def fetch_messages():
    query = (
        db.collection("rooms")
        .document(room_id)
        .collection("messages")
        .order_by("timestamp", direction=firestore.Query.ASCENDING)
    )

    if st.session_state.last_timestamp:
        query = query.where("timestamp", ">", st.session_state.last_timestamp)

    new_msgs = list(query.stream())

    if new_msgs:
        st.session_state.messages_cache.extend(new_msgs)
        last_data = new_msgs[-1].to_dict()
        st.session_state.last_timestamp = last_data.get("timestamp")


# Initial load
if not st.session_state.messages_cache:
    initial = (
        db.collection("rooms")
        .document(room_id)
        .collection("messages")
        .order_by("timestamp", direction=firestore.Query.ASCENDING)
        .limit(50)
        .stream()
    )
    st.session_state.messages_cache = list(initial)

    if st.session_state.messages_cache:
        last_data = st.session_state.messages_cache[-1].to_dict()
        st.session_state.last_timestamp = last_data.get("timestamp")

fetch_messages()

messages = st.session_state.messages_cache


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
.chat-bubble {
    padding: 8px 12px;
    border-radius: 14px;
    margin: 4px 0;
    max-width: 70%;
    font-size: 14px;
}
.sent {
    background: #005c4b;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.received {
    background: #1f2c34;
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}
.grouped {
    margin-top: 2px;
}
.chat-user {
    font-size: 12px;
    font-weight: 600;
    opacity: 0.85;
    margin-bottom: 2px;
}
.chat-translation {
    font-size: 11px;
    opacity: 0.6;
    margin-top: 3px;
}
.chat-time {
    font-size: 10px;
    opacity: 0.4;
    text-align: right;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RENDER CHAT
# ─────────────────────────────────────────────
previous_user = None

for msg in messages:
    data = msg.to_dict()

    timestamp = data.get("timestamp")
    time_str = timestamp.strftime("%H:%M") if timestamp else ""

    # strip_tags cleans any legacy HTML-polluted messages from Firestore
    user   = html.escape(strip_tags(data.get("user", "")))
    text   = html.escape(strip_tags(data.get("text", "")))
    transl = html.escape(strip_tags(data.get("translated", "")))

    is_me = user == html.escape(st.session_state.username)
    css = "sent" if is_me else "received"
    grouped = "grouped" if user == previous_user else ""

    name_html = f'<div class="chat-user">{user}</div>' if user != previous_user else ""

    st.markdown(
        f'<div class="chat-bubble {css} {grouped}">'
        f'{name_html}'
        f'<div>{text}</div>'
        f'<div class="chat-translation">→ {transl}</div>'
        f'<div class="chat-time">{time_str}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    previous_user = user


# ─────────────────────────────────────────────
# AUTO-SCROLL
# ─────────────────────────────────────────────
st.markdown("<div id='bottom'></div>", unsafe_allow_html=True)
st.markdown("""
<script>
    const el = window.parent.document.getElementById('bottom');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])

    with col1:
        message = st.text_input("Type message", label_visibility="collapsed")

    with col2:
        send = st.form_submit_button("➤")

    if send:
        send_message(message)
        st.rerun()


# ─────────────────────────────────────────────
# AUTO-REFRESH (st.fragment — Streamlit 1.33+)
# ─────────────────────────────────────────────
@st.fragment(run_every=3)
def poll_new_messages():
    """
    Only this fragment re-runs every 3 seconds.
    The input box, language selectors, and username field
    are outside this fragment and remain completely stable.
    """
    fetch_messages()

poll_new_messages()