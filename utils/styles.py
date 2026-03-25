"""
Shared CSS Styles
================
Loads and injects shared CSS into Streamlit pages.
"""

import streamlit as st
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

_CSS_CACHE = None


def load_css():
    """Load and inject shared CSS styles into the current page."""
    global _CSS_CACHE

    if _CSS_CACHE is None:
        css_path = Path(__file__).parent.parent / 'assets' / 'styles.css'
        try:
            _CSS_CACHE = css_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            logger.warning(f"CSS file not found at {css_path}")
            _CSS_CACHE = ""

    if _CSS_CACHE:
        st.markdown(f"<style>{_CSS_CACHE}</style>", unsafe_allow_html=True)
