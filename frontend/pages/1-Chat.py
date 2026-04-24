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
# LAYOUT CSS
# Forces Streamlit's wrapper divs into a full-height
# flex column: top bar | scrolling messages | input bar
# ─────────────────────────────────────────────
st.markdown("""
<style>

/* Kill Streamlit chrome */
#MainMenu, footer, header { display: none !important; }

/* Full viewport, no overflow */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Main block — flex column filling full height */
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main .block-container {
    height: 100vh !important;
    max-height: 100vh !important;
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}

/* ── Zone 1: top bar ── */
#top-bar {
    flex-shrink: 0;
    background: #111b21;
    border-bottom: 1px solid #2a3942;
    padding: 10px 16px;
    z-index: 10;
}
#top-bar > div,
#top-bar [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}

/* ── Zone 2: message area — grows and scrolls ── */
#chat-window {
    flex: 1 1 auto;
    overflow-y: auto;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    background: #0b141a;
    scrollbar-width: thin;
    scrollbar-color: #2a3942 transparent;
}
#chat-window::-webkit-scrollbar { width: 4px; }
#chat-window::-webkit-scrollbar-thumb {
    background: #2a3942;
    border-radius: 4px;
}

/* ── Zone 3: input bar — never moves ── */
#input-bar {
    flex-shrink: 0;
    background: #202c33;
    border-top: 1px solid #2a3942;
    padding: 10px 16px 14px 16px;
    z-index: 10;
}
#input-bar > div,
#input-bar [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}

/* ── Bubbles ── */
.chat-bubble {
    padding: 8px 12px;
    border-radius: 14px;
    max-width: 70%;
    font-size: 14px;
    word-wrap: break-word;
    line-height: 1.4;
}
.sent {
    background: #005c4b;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}
.received {
    background: #1f2c34;
    color: white;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}
.grouped { margin-top: 1px; }
.chat-user {
    font-size: 11px;
    font-weight: 600;
    opacity: 0.75;
    margin-bottom: 3px;
}
.chat-translation {
    font-size: 11px;
    opacity: 0.55;
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
# ZONE 1 — TOP BAR (name + language selectors)
# ─────────────────────────────────────────────
st.markdown('<div id="top-bar">', unsafe_allow_html=True)

st.session_state.username = st.text_input(
    "Your name",
    value=st.session_state.username,
    placeholder="Enter your name..."
)

col1, col2 = st.columns(2)
with col1:
    source_name = st.selectbox("Translate from", list(LANGUAGES.keys()))
with col2:
    target_name = st.selectbox("Translate to", list(LANGUAGES.keys()))

st.session_state.source_lang = LANGUAGES[source_name]
st.session_state.target_lang = LANGUAGES[target_name]

st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.username:
    st.markdown(
        '<div style="color:#8696a0;padding:20px;text-align:center;">'
        'Enter your name above to start chatting'
        '</div>',
        unsafe_allow_html=True
    )
    st.stop()


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
        st.session_state.last_timestamp = new_msgs[-1].to_dict().get("timestamp")


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
        st.session_state.last_timestamp = (
            st.session_state.messages_cache[-1].to_dict().get("timestamp")
        )

fetch_messages()
messages = st.session_state.messages_cache


# ─────────────────────────────────────────────
# ZONE 2 — MESSAGE AREA
# ─────────────────────────────────────────────
st.markdown('<div id="chat-window">', unsafe_allow_html=True)

previous_user = None

for msg in messages:
    data = msg.to_dict()

    timestamp = data.get("timestamp")
    time_str = timestamp.strftime("%H:%M") if timestamp else ""

    user   = html.escape(strip_tags(data.get("user", "")))
    text   = html.escape(strip_tags(data.get("text", "")))
    transl = html.escape(strip_tags(data.get("translated", "")))

    is_me   = user == html.escape(st.session_state.username)
    css     = "sent" if is_me else "received"
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

st.markdown('<div id="bottom"></div></div>', unsafe_allow_html=True)

# Scroll to bottom of chat-window (not the page)
st.markdown("""
<script>
    (function() {
        const win = document.getElementById('chat-window');
        if (win) win.scrollTop = win.scrollHeight;
    })();
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ZONE 3 — INPUT BAR
# ─────────────────────────────────────────────
st.markdown('<div id="input-bar">', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])
    with col1:
        message = st.text_input(
            "Type message",
            label_visibility="collapsed",
            placeholder="Type a message..."
        )
    with col2:
        send = st.form_submit_button("➤")
    if send:
        send_message(message)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# AUTO-REFRESH
# ─────────────────────────────────────────────
@st.fragment(run_every=3)
def poll_new_messages():
    fetch_messages()

poll_new_messages()
