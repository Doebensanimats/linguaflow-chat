from components.styles import load_css
from components.navbar import render_navbar
from components.layout import render_topbar, start_page, end_page


def page(title: str, subtitle: str = ""):
    load_css()
    render_navbar()
    render_topbar(title, subtitle)
    start_page()


def end():
    end_page()