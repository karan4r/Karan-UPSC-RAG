import streamlit as st
import json
from pathlib import Path

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global Dark Background */
    .stApp {
        background: #0B0F19 !important;
        font-family: 'Inter', sans-serif !important;
        color: #F8FAFC !important;
    }

    /* Force all text elements to crisp white/light contrast */
    html, body, p, span, div, li, label, .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #F8FAFC !important;
    }

    /* Headings styling */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Form & Input Labels */
    label, div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span {
        color: #38BDF8 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1240px !important;
    }

    /* Futuristic Header Banner */
    .futuristic-header {
        background: linear-gradient(135deg, #162032 0%, #0F172A 100%);
        border: 1px solid #38BDF8;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(0, 240, 255, 0.15);
    }

    .header-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
        margin: 0;
    }

    .header-subtitle {
        font-size: 0.95rem;
        color: #CBD5E1 !important;
        margin-top: 6px;
    }

    /* Status Badges */
    .status-badge-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 14px;
    }

    .status-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-flex;
        align-items: center;
    }

    .badge-cyan {
        background: #0C4A6E;
        border: 1px solid #38BDF8;
        color: #38BDF8 !important;
    }

    .badge-violet {
        background: #312E81;
        border: 1px solid #818CF8;
        color: #C7D2FE !important;
    }

    .badge-emerald {
        background: #064E3B;
        border: 1px solid #34D399;
        color: #A7F3D0 !important;
    }

    .badge-amber {
        background: #78350F;
        border: 1px solid #FBBF24;
        color: #FDE68A !important;
    }

    /* Glassmorphism Metric Cards */
    .metric-card {
        background: #162032;
        border: 1px solid #38BDF8;
        border-radius: 14px;
        padding: 18px 22px;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #38BDF8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-top: 4px;
    }

    /* Navigation Radio Horizontal Styling */
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        gap: 12px !important;
        background: #162032 !important;
        padding: 10px 14px !important;
        border-radius: 14px !important;
        border: 1px solid #38BDF8 !important;
    }

    div[data-testid="stRadio"] label {
        background: #0F172A !important;
        border-radius: 10px !important;
        padding: 10px 22px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: #E2E8F0 !important;
        cursor: pointer !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.5) !important;
    }

    /* Selectbox & Dropdown styling for high contrast */
    div[data-baseweb="select"] {
        background-color: #1E293B !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #1E293B !important;
        border: 1px solid #38BDF8 !important;
    }

    div[data-baseweb="option"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    div[data-baseweb="option"]:hover {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* Text inputs */
    div[data-baseweb="input"] {
        background-color: #1E293B !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] input {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    /* Expanders styling */
    div[data-testid="stExpander"] {
        background: #162032 !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 12px !important;
        margin-bottom: 14px !important;
    }

    div[data-testid="stExpander"] summary {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    div[data-testid="stExpander"] p, div[data-testid="stExpander"] span, div[data-testid="stExpander"] li {
        color: #F8FAFC !important;
    }

    /* Chat Messages styling */
    div[data-testid="stChatMessage"] {
        background: #162032 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin-bottom: 16px !important;
    }

    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li {
        color: #F8FAFC !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background: #0C4A6E !important;
        border: 1px solid #38BDF8 !important;
    }

    /* Custom Chat Input */
    div[data-testid="stChatInput"] input {
        border-radius: 14px !important;
        border: 1.5px solid #38BDF8 !important;
        background: #0F172A !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        background: #1E293B !important;
        border: 1px solid #38BDF8 !important;
        color: #38BDF8 !important;
        padding: 8px 16px !important;
    }

    .stButton>button:hover {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #38BDF8 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.6) !important;
    }

    /* Progress bar custom styling */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #38BDF8 0%, #6366F1 50%, #10B981 100%) !important;
    }

    /* Info and Warning boxes */
    div[data-testid="stAlert"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 12px !important;
    }

    div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {
        color: #F8FAFC !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_futuristic_header():
    st.markdown("""
    <div class="futuristic-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <h1 class="header-title">⚡ UPSC RAG MENTOR</h1>
                <div class="header-subtitle">Futuristic AI Copilot & GS Mains Microtopic Dashboard · CSE 2026-27</div>
            </div>
        </div>
        <div class="status-badge-container">
            <span class="status-badge badge-cyan">🟢 RAG NEURAL ENGINE ONLINE</span>
            <span class="status-badge badge-violet">⚡ 623 SYLLABUS NODES INDEXED</span>
            <span class="status-badge badge-emerald">📚 MAINS GS1-GS4 COVERAGE</span>
            <span class="status-badge badge-amber">🎯 TARGET: UPSC CSE 2026/27</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
