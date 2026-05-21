"""
Injects custom CSS into the Streamlit app.
Clean white background, Inter font, professional design — no emojis.
"""

import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #ffffff !important;
    color: #1a1a2e !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #ffffff !important;
}

[data-testid="block-container"] {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #f8f9fc !important;
    border-right: 1px solid #e5e7eb !important;
}

[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
    color: #1a1a2e !important;
}

.sidebar-logo {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #1a1a2e !important;
    padding: 0.5rem 0;
}

/* ── Typography ──────────────────────────────────────────────── */
.main-title {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #1a1a2e;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}

.main-subtitle {
    font-size: 0.95rem;
    font-weight: 400;
    color: #6b7280;
    margin-top: 0;
    margin-bottom: 1.5rem;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: #1a1a2e !important;
}

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    border-radius: 8px !important;
    border: 1px solid #d1d5db !important;
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}

.stButton > button:hover {
    background-color: #1a1a2e !important;
    color: #ffffff !important;
    border-color: #1a1a2e !important;
    box-shadow: 0 4px 12px rgba(26,26,46,0.15) !important;
}

/* ── Chat Messages ───────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background-color: #f8f9fc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
}

[data-testid="stChatMessage"][data-testid*="user"] {
    background-color: #f0f4ff !important;
    border-color: #c7d2fe !important;
}

[data-testid="stChatMessageContent"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.65 !important;
    color: #1a1a2e !important;
}

/* ── Chat Input ──────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    border: 1.5px solid #d1d5db !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    background-color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}

/* ── Chunk Cards ─────────────────────────────────────────────── */
.chunk-card {
    background: #f8f9fc;
    border: 1px solid #e5e7eb;
    border-left: 3px solid #2563eb;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
}

.chunk-source {
    font-size: 0.75rem;
    font-weight: 600;
    color: #2563eb;
    display: block;
    margin-bottom: 0.35rem;
    letter-spacing: 0.01em;
}

.chunk-text {
    font-size: 0.82rem;
    color: #4b5563;
    line-height: 1.55;
    margin: 0;
}

/* ── Badges ──────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    margin-top: 0.4rem;
    letter-spacing: 0.03em;
}

.badge-green {
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #6ee7b7;
}

.badge-red {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
}

/* ── Metrics ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #f8f9fc !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #1a1a2e !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    color: #6b7280 !important;
}

/* ── Tabs ────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #6b7280 !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #1a1a2e !important;
    border-bottom: 2px solid #2563eb !important;
}

/* ── Inputs & Selects ────────────────────────────────────────── */
input, textarea, select,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: 8px !important;
    border: 1px solid #d1d5db !important;
    color: #1a1a2e !important;
    background-color: #ffffff !important;
}

input:focus, textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    outline: none !important;
}

/* ── Dataframe ───────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Expander ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    background-color: #fafafa !important;
}

/* ── Divider ─────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid #e5e7eb !important;
    margin: 1rem 0 !important;
}

/* ── Scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── File Uploader ───────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed #d1d5db !important;
    border-radius: 12px !important;
    background-color: #fafafa !important;
    padding: 1rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #2563eb !important;
    background-color: #f0f4ff !important;
}

/* ── Alerts ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Spinner ─────────────────────────────────────────────────── */
[data-testid="stSpinner"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    color: #6b7280 !important;
}

/* ── Selectbox ───────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border-color: #d1d5db !important;
    font-family: 'Inter', sans-serif !important;
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# Auto-inject when imported
inject_css()
