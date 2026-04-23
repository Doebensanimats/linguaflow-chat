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
from streamlit_autorefresh import st_autorefresh

# ensure project root is accessible
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from services.api_client import translate
from config.settings import FIREBASE_KEY_PATH


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LinguaFlow Chat",
    layout="wide"
)


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "username" not in st.session_state:
    st.session_state.username = ""


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
# ROOM HANDLING
# ─────────────────────────────────────────────
room_id = st.query_params.get("room", None)

if not room_id:
    st.title("🌐 LinguaFlow Chat")

    if st.button("🚀 Create Chat Room"):
        new_room = str(uuid.uuid4())[:6]
        st.query_params["room"] = new_room
        st.rerun()

    st.stop()


# ─────────────────────────────────────────────
# HEADER / USER
# ─────────────────────────────────────────────
st.title(f"💬 Room: {room_id}")

st.session_state.username = st.text_input(
    "Enter your name",
    value=st.session_state.username
)

if not st.session_state.username:
    st.stop()


# ─────────────────────────────────────────────
# SEND MESSAGE
# ─────────────────────────────────────────────
def send_message(text: str):
    text = text.strip()
    if not text:
        return

    translated = translate(text, "en", "es")

    db.collection("rooms") \
      .document(room_id) \
      .collection("messages") \
      .add({
          "user": st.session_state.username,
          "text": text,
          "translated": translated,
          "timestamp": datetime.now(timezone.utc)
      })


# ─────────────────────────────────────────────
# LOAD MESSAGES
# ─────────────────────────────────────────────
messages_ref = (
    db.collection("rooms")
    .document(room_id)
    .collection("messages")
    .order_by("timestamp", direction=firestore.Query.DESCENDING)
    .limit(50)
)

messages = list(messages_ref.stream())
messages.reverse()


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
.chat-bubble {
    padding: 10px 14px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.4;
    word-wrap: break-word;
}

.sent {
    background: #005c4b;
    color: white;
    margin-left: auto;
    text-align: right;
}

.received {
    background: #1f2c34;
    color: white;
    margin-right: auto;
    text-align: left;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RENDER CHAT
# ─────────────────────────────────────────────
for msg in messages:
    data = msg.to_dict()

    is_me = data.get("user") == st.session_state.username
    css = "sent" if is_me else "received"

    st.markdown(f"""
    <div class="chat-bubble {css}">
        <b>{html.escape(data.get("user", ""))}</b><br>
        {html.escape(data.get("text", ""))}
        <div style="font-size:11px; opacity:0.7;">
            → {html.escape(data.get("translated", ""))}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])

    with col1:
        message = st.text_input(
            "Type message",
            label_visibility="collapsed"
        )

    with col2:
        send = st.form_submit_button("➤")

    if send:
        send_message(message)
        st.rerun()


# ─────────────────────────────────────────────
# AUTO REFRESH
# ─────────────────────────────────────────────
st_autorefresh(interval=3000, key="chat_refresh")