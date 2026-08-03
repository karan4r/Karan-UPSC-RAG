import streamlit as st
import json
from pathlib import Path

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Outfit:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Next-Gen Dark Cyber Background */
    .stApp {
        background-color: #060812 !important;
        background-image: 
            radial-gradient(at 15% 15%, rgba(14, 165, 233, 0.08) 0px, transparent 50%),
            radial-gradient(at 85% 85%, rgba(139, 92, 246, 0.08) 0px, transparent 50%) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #F8FAFC !important;
    }

    /* Force text elements to high-contrast clear white/light gray */
    html, body, p, span, div, li, label, .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #CBD5E1 !important;
    }

    /* Headings styling - Cyber Neon */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }

    /* Form & Input Labels */
    label, div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Layout */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1280px !important;
    }

    /* Sidebar Dark Glass Style */
    section[data-testid="stSidebar"] {
        background-color: #070916 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.2) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }

    /* Futuristic Cyber Header Banner */
    .futuristic-header {
        background: linear-gradient(135deg, rgba(13, 17, 32, 0.9) 0%, rgba(8, 11, 23, 0.95) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.3);
        border-radius: 20px;
        padding: 28px 34px;
        margin-bottom: 24px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.15);
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
        background: linear-gradient(90deg, #38BDF8, #8B5CF6, #EC4899, #10B981);
    }

    .header-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF 0%, #38BDF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
    }

    .header-subtitle {
        font-size: 0.95rem;
        color: #94A3B8 !important;
        margin-top: 6px;
        font-weight: 600;
        letter-spacing: 0.2px;
    }

    /* Cyber HUD Status Badges */
    .status-badge-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 18px;
    }

    .status-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }

    .badge-primary {
        background: rgba(14, 165, 233, 0.12);
        color: #38BDF8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399 !important;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }

    .badge-purple {
        background: rgba(139, 92, 246, 0.12);
        color: #C084FC !important;
        border: 1px solid rgba(192, 132, 252, 0.3);
    }

    /* High Visibility Glowing Cyber Query Box Container */
    form[key="top_query_form"], form[key^="query_form_"], div[data-testid="stForm"] {
        background: linear-gradient(135deg, rgba(13, 17, 32, 0.95) 0%, rgba(8, 11, 23, 0.98) 100%) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 18px !important;
        padding: 22px 26px !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.18) !important;
        margin-bottom: 24px !important;
    }

    form[key^="query_form_"] input, div[data-testid="stForm"] input {
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        background: #090D1A !important;
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
    }

    form[key^="query_form_"] input:focus, div[data-testid="stForm"] input:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.5) !important;
    }

    /* Cyber Neon Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #0284C7 0%, #7C3AED 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(2, 132, 199, 0.4) !important;
        transition: all 0.25s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(56, 189, 248, 0.6) !important;
        opacity: 0.95 !important;
    }

    /* Radio Tabs / Navigation Bar Styling */
    div[data-testid="stRadio"] > div,
    div[data-testid="stRadio"] [role="radiogroup"],
    div[data-testid="stWidgetGroup"] {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        background: rgba(13, 17, 32, 0.8) !important;
        padding: 8px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        width: 100% !important;
    }

    div[data-testid="stRadio"] label,
    div[role="radiogroup"] label {
        background: rgba(15, 23, 42, 0.6) !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        margin: 2px !important;
        display: inline-flex !important;
        align-items: center !important;
    }

    div[data-testid="stRadio"] label:hover,
    div[role="radiogroup"] label:hover {
        color: #FFFFFF !important;
        background: rgba(56, 189, 248, 0.15) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"],
    div[role="radiogroup"] label[aria-checked="true"],
    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.35) 0%, rgba(124, 58, 237, 0.35) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3) !important;
    }

    div[data-testid="stRadio"] label p,
    div[role="radiogroup"] label p,
    div[data-testid="stRadio"] label span,
    div[role="radiogroup"] label span {
        color: inherit !important;
        font-weight: inherit !important;
        font-size: 0.92rem !important;
    }

    /* Chat Message Bubbles in Cyber Dark Theme */
    div[data-testid="stChatMessage"] {
        background: rgba(13, 17, 32, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 22px 26px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li {
        color: #E2E8F0 !important;
        font-size: 0.98rem !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(13, 17, 32, 0.9) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }

    /* Expanders styling */
    div[data-testid="stExpander"] {
        background: rgba(9, 13, 26, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 14px !important;
        margin-bottom: 16px !important;
    }

    div[data-testid="stExpander"] summary {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(13, 17, 32, 0.75) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }

    .metric-label {
        font-size: 0.82rem !important;
        color: #94A3B8 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* PW Skills Cards */
    .pwskills-card {
        background: rgba(13, 17, 32, 0.75) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        margin-bottom: 16px !important;
        transition: all 0.25s ease !important;
    }

    .pwskills-card:hover {
        border-color: #38BDF8 !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.25) !important;
    }

    .pwskills-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF !important;
    }

    .pwskills-desc {
        font-size: 0.92rem;
        color: #CBD5E1 !important;
        margin-top: 6px;
        line-height: 1.5;
    }

    .pwskills-link {
        color: #38BDF8 !important;
        font-weight: 700;
        text-decoration: none;
    }

    .pwskills-link:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

def render_futuristic_header():
    st.markdown("""
    <div class="futuristic-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 class="header-title">⚡ UPSC AI NEURAL COPILOT</h1>
                <div class="header-subtitle">Quantum RAG Neural Engine · Real-time Syllabus Matrix & Psychological Copilot</div>
            </div>
            <div style="text-align: right;">
                <span style="font-family:'JetBrains Mono'; font-size:0.78rem; background:rgba(56,189,248,0.15); color:#38BDF8; padding:5px 12px; border-radius:12px; border:1px solid rgba(56,189,248,0.3); font-weight:700;">
                    MODEL: GROQ LLAMA 3.3 70B NEURAL
                </span>
            </div>
        </div>
        <div class="status-badge-container">
            <span class="status-badge badge-success">🟢 RAG NEURAL CORE: ONLINE</span>
            <span class="status-badge badge-primary">🧠 623 MAINS MICROTOPICS ACTIVE</span>
            <span class="status-badge badge-purple">🧘 MENTAL HEALTH & WELLNESS: ACTIVE</span>
            <span class="status-badge badge-success">📝 MOCK TESTS & CLASSES: READY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
