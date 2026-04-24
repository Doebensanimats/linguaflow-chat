# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime, timezone
import html
import sys
import os

# ensure project root is accessible
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from services.api_client import translate
from config.settings import FIREBASE_KEY_PATH
from config.Languages import LANGUAGES


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LinguaFlow Chat",
    layout="wide"
)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state.username = ""

if "source_lang" not in st.session_state:
    st.session_state.source_lang = "en"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "es"


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
st.title(f"Room: {room_id}")

st.session_state.username = st.text_input(
    "Name",
    value=st.session_state.username
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
# LOAD MESSAGES (NEWEST FIRST)
# ─────────────────────────────────────────────
messages_ref = (
    db.collection("rooms")
    .document(room_id)
    .collection("messages")
    .order_by("timestamp", direction=firestore.Query.DESCENDING)
    .limit(30)
)

messages = list(messages_ref.stream())


# ─────────────────────────────────────────────
# STYLES (MINIMAL SAFE)
# ─────────────────────────────────────────────
st.markdown("""
<style>
.chat-bubble {
    padding: 10px;
    border-radius: 10px;
    margin: 6px 0;
    max-width: 70%;
    font-size: 14px;
}

.sent {
    background: #005c4b;
    color: white;
    margin-left: auto;
}

.received {
    background: #1f2c34;
    color: white;
    margin-right: auto;
}

.time {
    font-size: 10px;
    opacity: 0.5;
    text-align: right;
    margin-top: 3px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RENDER CHAT (SAFE VERSION)
# ─────────────────────────────────────────────
for msg in messages:
    data = msg.to_dict()

    timestamp = data.get("timestamp")
    time_str = timestamp.strftime("%H:%M") if timestamp else ""

    is_me = data.get("user") == st.session_state.username
    css = "sent" if is_me else "received"

    user   = html.escape(str(data.get("user", "")))
    text   = html.escape(str(data.get("text", "")))
    transl = html.escape(str(data.get("translated", "")))

    st.markdown(
        f'<div class="chat-bubble {css}">'
        f'  <b>{user}</b><br>'
        f'  {text}<br>'
        f'  <span style="opacity:0.7">→ {transl}</span>'
        f'  <div class="time">{time_str}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
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