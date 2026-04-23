import streamlit as st
from components.styles import load_css
from components.navbar import render_navbar

import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="LinguaFlow",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL STYLES ─────────────────────────────────────────
load_css()

# ── SIDEBAR NAV ───────────────────────────────────────────
render_navbar()

# ── HERO SECTION ──────────────────────────────────────────
st.markdown("""
<div style="
  background: linear-gradient(135deg, #0F1923 0%, #1A2942 100%);
  padding: 4rem 3rem;
  border-radius: 16px;
  color: white;
">

  <h1 style="
    font-size: 3rem;
    font-family: 'Syne', sans-serif;
    margin-bottom: 1rem;
  ">
    Break Language Barriers 🌐
  </h1>

  <p style="
    font-size: 1.1rem;
    opacity: 0.7;
    max-width: 600px;
  ">
    Real-time multilingual chat, translation, voice, and documents — all in one AI platform.
  </p>

</div>
""", unsafe_allow_html=True)

# ── FEATURE CARDS ─────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 💬 Chat
    Real-time multilingual conversations with AI translation.
    """)

with col2:
    st.markdown("""
    ### 📄 Documents
    Translate PDFs, text, and files instantly.
    """)

with col3:
    st.markdown("""
    ### 🎤 Voice
    Speech-to-speech translation in real time.
    """)

# ── CTA ────────────────────────────────────────────────────
st.markdown("---")

st.markdown("""
### 🚀 Get Started
Use the sidebar to open:
- Chat
- Documents
- Audiobook
""")