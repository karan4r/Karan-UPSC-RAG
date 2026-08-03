import streamlit as st
import json
from pathlib import Path

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Outfit:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

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

    /* Headings styling - Futuristic & Expensive */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }

    /* Form & Input Labels */
    label, div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.2px !important;
    }

    /* Main Container Layout */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1240px !important;
    }

    /* Futuristic Header Banner */
    .futuristic-header {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 18px;
        padding: 26px 34px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(37, 99, 235, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.03);
        position: relative;
        overflow: hidden;
    }

    .futuristic-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2563EB, #6366F1, #8B5CF6, #10B981, #F59E0B);
    }

    .header-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0F172A 0%, #1D4ED8 50%, #6D28D9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
    }

    .header-subtitle {
        font-size: 0.95rem;
        color: #475569 !important;
        margin-top: 6px;
        font-weight: 600;
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
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.3px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
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
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }

    .metric-card:hover {
        border-color: #2563EB;
        transform: translateY(-2px);
    }

    .metric-label {
        font-size: 0.82rem;
        color: #2563EB !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif;
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
        border-radius: 16px !important;
        border: 1.5px solid #CBD5E1 !important;
        box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05) !important;
    }

    div[data-testid="stRadio"] label {
        background: #F8FAFC !important;
        border-radius: 10px !important;
        padding: 10px 22px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        cursor: pointer !important;
        border: 1px solid #E2E8F0 !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stRadio"] label:hover {
        color: #1D4ED8 !important;
        background: #EFF6FF !important;
        border-color: #BFDBFE !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label[data-checked="true"] span {
        color: #FFFFFF !important;
    }

    /* HIGH-VISIBILITY PROMINENT TOP QUERY CONTAINER FORM */
    form[key="top_query_form"], div[data-testid="stForm"] {
        background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%) !important;
        border: 2.5px solid #2563EB !important;
        border-radius: 18px !important;
        padding: 18px 24px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2), 0 2px 8px rgba(15, 23, 42, 0.05) !important;
    }

    form[key="top_query_form"] input, div[data-testid="stForm"] input {
        border: 2px solid #2563EB !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 14px !important;
        padding: 12px 18px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12) !important;
    }

    form[key="top_query_form"] input:focus, div[data-testid="stForm"] input:focus {
        border-color: #1D4ED8 !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
    }

    /* PROMINENT ULTRA-VISIBLE CHAT INPUT BAR */
    div[data-testid="stChatInput"] {
        padding: 8px !important;
    }

    div[data-testid="stChatInput"] input {
        border: 2px solid #2563EB !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 24px rgba(37, 99, 235, 0.2), 0 0 0 1px #3B82F6 !important;
        border-radius: 16px !important;
        padding: 16px 22px !important;
    }

    div[data-testid="stChatInput"] input:focus {
        border-color: #1D4ED8 !important;
        box-shadow: 0 8px 30px rgba(37, 99, 235, 0.35) !important;
    }

    /* PROMINENT SEARCH INPUT BAR IN DASHBOARD */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 2px solid #2563EB !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12) !important;
    }

    div[data-baseweb="input"] input {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* Selectboxes & Dropdowns */
    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="select"] * {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #2563EB !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
    }

    div[data-baseweb="option"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    div[data-baseweb="option"]:hover {
        background-color: #EFF6FF !important;
        color: #1D4ED8 !important;
    }

    /* Expanders styling */
    div[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 14px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03) !important;
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
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
    }

    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li {
        color: #0F172A !important;
        font-size: 0.98rem !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background: #EFF6FF !important;
        border: 1.5px solid #BFDBFE !important;
    }

    /* Executive Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        color: #0F172A !important;
        padding: 9px 20px !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3) !important;
    }

    /* PW Skills Card styling */
    .pwskills-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
        transition: all 0.2s ease;
    }

    .pwskills-card:hover {
        border-color: #2563EB;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12);
    }

    .pwskills-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
    }

    .pwskills-desc {
        font-size: 0.9rem;
        color: #475569;
        margin-top: 6px;
    }

    .pwskills-link {
        color: #2563EB;
        font-weight: 700;
        text-decoration: none;
    }

    .pwskills-link:hover {
        text-decoration: underline;
    }

    /* Progress bar custom styling */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #2563EB 0%, #6366F1 50%, #10B981 100%) !important;
    }

    /* Alert Boxes */
    div[data-testid="stAlert"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 14px !important;
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
                <h1 class="header-title">⚡ UPSC AI RAG MENTOR</h1>
                <div class="header-subtitle">Futuristic AI Copilot & GS Mains Curriculum Dashboard · CSE 2026-27</div>
            </div>
        </div>
        <div class="status-badge-container">
            <span class="status-badge badge-cyan"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#2563EB;"></span> RAG NEURAL ENGINE ONLINE</span>
            <span class="status-badge badge-violet">⚡ 623 SYLLABUS MODULES</span>
            <span class="status-badge badge-emerald">📚 GS1-GS4 MAINS COVERAGE</span>
            <span class="status-badge badge-amber">🎯 TARGET: UPSC CSE 2026/27</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
