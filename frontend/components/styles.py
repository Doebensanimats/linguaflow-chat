import streamlit as st
from pathlib import Path

def load_css():
    base_path = Path(__file__).parent / "styles"

    files = [
        "base.css",
        "layout.css",
        "components.css",
        "overrides.css",
    ]

    css = ""
    for f in files:
        with open(base_path / f) as file:
            css += file.read()

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)