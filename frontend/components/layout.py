import streamlit as st

def render_topbar(title, subtitle=""):
    st.markdown(f"""
    <div class="lf-topbar">
        <div>
            <div class="lf-topbar-title">{title}</div>
            <div class="lf-topbar-sub">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def start_page():
    st.markdown('<div class="lf-content">', unsafe_allow_html=True)


def end_page():
    st.markdown('</div>', unsafe_allow_html=True)