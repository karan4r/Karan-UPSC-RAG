import streamlit as st
import json
from pathlib import Path

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Cinzel:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Light Alabaster Background */
    .stApp {
        background-color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #0F172A !important;
    }

    /* Force all text elements to clean, high-contrast dark charcoal */
    html, body, p, span, div, li, label, .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #0F172A !important;
    }

    /* Headings styling - Sophisticated & Expensive */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }

    /* Form & Input Labels */
    label, div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.2px !important;
    }

    /* Main Container Layout */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }

    /* Elite Header Banner */
    .futuristic-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 26px 34px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.04), 0 4px 12px -2px rgba(15, 23, 42, 0.02);
        position: relative;
        overflow: hidden;
    }

    .futuristic-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1E3A8A, #2563EB, #D97706, #059669);
    }

    .header-title {
        font-family: 'Cinzel', serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A !important;
        letter-spacing: 1.5px;
        margin: 0;
    }

    .header-subtitle {
        font-size: 0.92rem;
        color: #64748B !important;
        margin-top: 6px;
        font-weight: 500;
        letter-spacing: 0.2px;
    }

    /* Status Badges - Refined Executive Chips */
    .status-badge-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 16px;
    }

    .status-badge {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 600;
        letter-spacing: 0.3px;
        display: inline-flex;
        align-items: center;
    }

    .badge-cyan {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1D4ED8 !important;
    }

    .badge-violet {
        background: #F5F3FF;
        border: 1px solid #DDD6FE;
        color: #6D28D9 !important;
    }

    .badge-emerald {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        color: #047857 !important;
    }

    .badge-amber {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        color: #B45309 !important;
    }

    /* Minimalist Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.03);
    }

    .metric-label {
        font-size: 0.8rem;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .metric-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A !important;
        margin-top: 4px;
    }

    /* Top Segmented Navigation Pills */
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        gap: 10px !important;
        background: #FFFFFF !important;
        padding: 8px 12px !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.04) !important;
    }

    div[data-testid="stRadio"] label {
        background: #F8FAFC !important;
        border-radius: 10px !important;
        padding: 9px 22px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        cursor: pointer !important;
        border: 1px solid #E2E8F0 !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stRadio"] label:hover {
        color: #1E293B !important;
        background: #EDF2F7 !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label[data-checked="true"] span {
        color: #FFFFFF !important;
    }

    /* Selectboxes & Dropdowns */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] * {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
    }

    div[data-baseweb="option"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    div[data-baseweb="option"]:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }

    /* Text Inputs */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] input {
        color: #0F172A !important;
        font-weight: 500 !important;
    }

    /* Expanders styling */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02) !important;
    }

    div[data-testid="stExpander"] summary {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    div[data-testid="stExpander"] p, div[data-testid="stExpander"] span, div[data-testid="stExpander"] li {
        color: #1E293B !important;
    }

    /* Chat Messages styling */
    div[data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03) !important;
    }

    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li {
        color: #0F172A !important;
        font-size: 0.98rem !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Custom Chat Input */
    div[data-testid="stChatInput"] input {
        border-radius: 14px !important;
        border: 1px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 0.98rem !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04) !important;
    }

    /* Executive Buttons */
    .stButton>button {
        border-radius: 10px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border-color: #0F172A !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
    }

    /* Progress bar custom styling */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #1E3A8A 0%, #2563EB 50%, #059669 100%) !important;
    }

    /* Info and Warning boxes */
    div[data-testid="stAlert"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
    }

    div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {
        color: #0F172A !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_futuristic_header():
    st.markdown("""
    <div class="futuristic-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <h1 class="header-title">🏛️ UPSC MAINS COPILOT</h1>
                <div class="header-subtitle">Executive AI Mentor & Microtopic Curriculum Navigator · CSE 2026-27</div>
            </div>
        </div>
        <div class="status-badge-container">
            <span class="status-badge badge-cyan">🟢 RAG KNOWLEDGE CORE</span>
            <span class="status-badge badge-violet">⚡ 623 SYLLABUS MODULES</span>
            <span class="status-badge badge-emerald">📚 GS1-GS4 MAINS COVERAGE</span>
            <span class="status-badge badge-amber">🎯 TARGET: UPSC CSE 2026/27</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
