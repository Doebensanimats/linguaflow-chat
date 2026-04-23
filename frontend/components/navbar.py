def render_navbar(active_page="Home"):
    import streamlit as st

    st.sidebar.title("🌐 LinguaFlow")

    if st.sidebar.button("🏠 Home"):
        st.switch_page("app.py")

    if st.sidebar.button("💬 Chat"):
        st.switch_page("pages/1_Chat.py")

    if st.sidebar.button("📄 Documents"):
        st.switch_page("pages/2_Document_Translator.py")

    if st.sidebar.button("🎧 Audiobook"):
        st.switch_page("pages/3_Audiobook.py")

    st.sidebar.markdown("---")
    st.sidebar.write(f"Current: **{active_page}**")


def render_page_header(title, subtitle=None):
    import streamlit as st

    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"<p style='color:gray'>{subtitle}</p>", unsafe_allow_html=True)