import streamlit as st
import json
from pathlib import Path

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Background - Minimalist Crisp Light Canvas */
    .stApp {
        background-color: #F8FAFC !important;
        background-image: none !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #1E293B !important;
    }

    /* Main Container Layout */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
    }

    /* Clean Light Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 2px 0 12px rgba(0, 0, 0, 0.02) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #334155 !important;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #475569 !important;
        font-weight: 600 !important;
    }

    /* Typography Defaults */
    html, body, p, span, div, li, label, td, th {
        color: #334155;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* Minimalist Top Bar */
    .minimal-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 12px 24px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    .topbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .topbar-logo-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    .topbar-logo-sub {
        font-size: 0.72rem;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Greeting Hero Banner */
    .greeting-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 28px 34px;
        margin-bottom: 22px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03);
    }

    .greeting-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        margin: 0 0 6px 0 !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .greeting-tagline {
        font-size: 1.05rem;
        font-weight: 600;
        color: #334155;
        margin: 0 0 4px 0;
    }

    .greeting-desc {
        font-size: 0.92rem;
        color: #64748B;
        margin: 0;
        line-height: 1.5;
    }

    /* Search Omnibar */
    .omnibar-wrapper {
        margin-bottom: 24px;
    }

    /* Search Omnibar */
    div[data-testid="stForm"]:has(input[aria-label*="omnibar"]),
    div[data-testid="stForm"]:has(input[placeholder*="Ask anything about UPSC"]) {
        background: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 9999px !important;
        padding: 4px 10px 4px 20px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stForm"]:has(input[placeholder*="Ask anything about UPSC"]):focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.12) !important;
    }

    div[data-testid="stForm"]:has(input[placeholder*="Ask anything about UPSC"]) input {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        font-size: 0.96rem !important;
        color: #1E293B !important;
    }

    div[data-testid="stForm"]:has(input[placeholder*="Ask anything about UPSC"]) .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        font-size: 1.1rem !important;
    }

    div[data-testid="stForm"]:has(input[placeholder*="Ask anything about UPSC"]) .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4) !important;
    }

    /* Grid of Pastel Minimalist Cards */
    .feature-card {
        border-radius: 18px;
        padding: 20px 22px;
        min-height: 145px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.05);
    }

    /* Column buttons below feature cards */
    div[data-testid="stColumn"]:has(.feature-card) .stButton > button {
        border-radius: 9999px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        padding: 6px 14px !important;
        margin-top: 4px !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        background: #FFFFFF !important;
        color: #334155 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }

    div[data-testid="stColumn"]:has(.feature-card) .stButton > button:hover {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border-color: #0F172A !important;
        transform: translateY(-1px) !important;
    }

    /* Card Themes */
    .card-copilot {
        background-color: #F0F6FF;
        border: 1px solid #DBEAFE;
    }
    .card-syllabus {
        background-color: #F0FDF4;
        border: 1px solid #DCFCE7;
    }
    .card-planner {
        background-color: #FFFBEB;
        border: 1px solid #FEF3C7;
    }
    .card-productivity {
        background-color: #F0F9FF;
        border: 1px solid #E0F2FE;
    }
    .card-relationship {
        background-color: #FFF1F2;
        border: 1px solid #FFE4E6;
    }
    .card-wellness {
        background-color: #F0FDFA;
        border: 1px solid #CCFBF1;
    }
    .card-mock {
        background-color: #FAF5FF;
        border: 1px solid #F3E8FF;
    }
    .card-classes {
        background-color: #FDF2F8;
        border: 1px solid #FCE7F3;
    }
    .card-pwskills {
        background-color: #F0F9FF;
        border: 1px solid #E0F2FE;
    }

    .card-icon-badge {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        margin-bottom: 14px;
        background: #FFFFFF;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }

    .card-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 6px 0;
        line-height: 1.3;
    }

    .card-desc {
        font-size: 0.83rem;
        color: #64748B;
        margin: 0 0 12px 0;
        line-height: 1.45;
        flex-grow: 1;
    }

    .card-footer {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    .card-arrow {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748B;
        font-size: 0.85rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }

    .feature-card:hover .card-arrow {
        background: #0F172A;
        color: #FFFFFF;
        transform: translateX(2px);
    }

    /* Wide Mission Banner */
    .mission-banner {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 24px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
    }

    .mission-tag {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .mission-headline {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.65rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0;
    }

    /* Right Widget Column Cards */
    .widget-panel-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
    }

    .widget-panel-title {
        font-size: 0.96rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 14px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Progress Donut Chart Styling */
    .progress-matrix-container {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 14px;
    }

    .progress-donut-wrapper {
        position: relative;
        width: 82px;
        height: 82px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .progress-donut-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .progress-list-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        margin-bottom: 6px;
    }

    .progress-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }

    /* Focus Checklist Items */
    .focus-task-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        font-size: 0.88rem;
        color: #334155;
        border-bottom: 1px solid #F1F5F9;
    }

    .focus-task-item:last-child {
        border-bottom: none;
    }

    /* Clean Streamlit Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
        border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        color: #334155 !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02) !important;
    }

    .stButton>button:hover {
        background: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04) !important;
    }

    .stButton>button:active {
        transform: translateY(0) !important;
    }

    /* Primary Accent Buttons */
    div[data-testid="stForm"] .stButton>button,
    button[kind="primary"],
    .primary-btn button {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #4338CA !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }

    div[data-testid="stForm"] .stButton>button:hover,
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338CA 0%, #3730A3 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35) !important;
    }

    /* Minimalist Inputs & Forms */
    div[data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
    }

    input, textarea, div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
        border-radius: 10px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    input:focus, textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    /* Clean Chat Messages */
    div[data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background-color: #EEF2FF !important;
        border: 1px solid #E0E7FF !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
    }

    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] span, 
    div[data-testid="stChatMessage"] li {
        color: #1E293B !important;
        line-height: 1.65 !important;
    }

    /* Clean Expanders */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stExpander"] summary {
        color: #0F172A !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }

    /* Clean Metric Cards */
    .metric-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 18px 20px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    }

    .metric-value {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .metric-label {
        font-size: 0.8rem !important;
        color: #64748B !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        margin-bottom: 4px !important;
    }

    /* Clean Progress Bars */
    div[data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, #4F46E5 0%, #6366F1 100%) !important;
        border-radius: 9999px !important;
    }

    div[data-testid="stProgress"] > div > div {
        background-color: #E2E8F0 !important;
        border-radius: 9999px !important;
        height: 8px !important;
    }

    /* Minimalist Pill Badges */
    .status-badge {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .badge-primary {
        background: #EFF6FF !important;
        color: #2563EB !important;
        border: 1px solid #BFDBFE !important;
    }

    .badge-success {
        background: #F0FDF4 !important;
        color: #16A34A !important;
        border: 1px solid #BBF7D0 !important;
    }

    .badge-purple {
        background: #FAF5FF !important;
        color: #9333EA !important;
        border: 1px solid #E9D5FF !important;
    }

    .badge-amber {
        background: #FFFBEB !important;
        color: #D97706 !important;
        border: 1px solid #FDE68A !important;
    }

    /* Minimalist Header Banner for Inner Pages */
    .minimal-page-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }

    .minimal-page-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .minimal-page-desc {
        font-size: 0.88rem;
        color: #64748B;
        margin: 4px 0 0 0;
    }

    /* Hide redundant Streamlit UI chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 100 !important;
    }

    /* Navigation Radio Pills */
    div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 4px !important;
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    div[data-testid="stRadio"] label {
        background-color: transparent !important;
        border-radius: 10px !important;
        padding: 8px 14px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        cursor: pointer !important;
        border: none !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stRadio"] label:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        background-color: #EEF2FF !important;
        color: #4338CA !important;
        font-weight: 700 !important;
    }

    /* PW Skills Card Minimalist */
    .pwskills-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
    }

    .pwskills-card:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04) !important;
    }

    .pwskills-title {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    .pwskills-desc {
        font-size: 0.88rem !important;
        color: #64748B !important;
        margin-top: 6px !important;
        line-height: 1.5 !important;
    }

    .pwskills-link {
        color: #4F46E5 !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }

    .pwskills-link:hover {
        text-decoration: underline !important;
    }
    </style>
    """, unsafe_allow_html=True)


EXAM_META_CONFIG = {
    "UPSC": {
        "title": "UPSC Civil Services Examination",
        "subtitle": "IAS / IPS / IFS · High-Yield GS Microtopics & RAG Mentor",
        "tag": "UPSC CSE",
        "badges": [
            ("🟢 RAG Core Active", "badge-success"),
            ("🧠 623 Microtopics", "badge-primary"),
            ("🧘 Wellness Active", "badge-purple"),
            ("📝 Prelims & Mains Ready", "badge-amber")
        ]
    },
    "IIT-JEE": {
        "title": "IIT-JEE Engineering Copilot",
        "subtitle": "JEE Main & Advanced · Physics, Chemistry & Mathematics",
        "tag": "IIT-JEE",
        "badges": [
            ("🟢 JEE Engine Active", "badge-success"),
            ("📐 Formulas Active", "badge-primary"),
            ("💡 Step-by-Step Solver", "badge-purple"),
            ("🎯 High-Yield Mocks", "badge-amber")
        ]
    },
    "NEET": {
        "title": "NEET UG Medical Copilot",
        "subtitle": "National Eligibility cum Entrance Test · NCERT Line-by-Line Engine",
        "tag": "NEET UG",
        "badges": [
            ("🟢 NCERT Matrix Online", "badge-success"),
            ("🧬 High-Yield Bio & Chem", "badge-primary"),
            ("🔬 Assertion-Reason", "badge-purple"),
            ("💡 Mnemonic Engine", "badge-amber")
        ]
    },
    "GATE": {
        "title": "GATE Engineering AI Copilot",
        "subtitle": "Graduate Aptitude Test in Engineering · Numerical Solver",
        "tag": "GATE",
        "badges": [
            ("🟢 Technical Core Online", "badge-success"),
            ("📊 NAT Answer Solver", "badge-primary"),
            ("💻 Core Matrix", "badge-purple"),
            ("⚡ Step-by-Step Logic", "badge-amber")
        ]
    },
    "CAT": {
        "title": "CAT Aptitude & DILR Master",
        "subtitle": "Common Admission Test · Speed Math & Logical Breakdown",
        "tag": "CAT IIM",
        "badges": [
            ("🟢 Strategy Matrix Online", "badge-success"),
            ("⚡ Speed Math Shortcuts", "badge-primary"),
            ("🧩 DILR Puzzle Matrix", "badge-purple"),
            ("📚 VARC Passage Analysis", "badge-amber")
        ]
    },
    "Banking": {
        "title": "Banking Exam AI Copilot",
        "subtitle": "IBPS & SBI PO/Clerk · Speed Aptitude & Financial Awareness",
        "tag": "Banking PO",
        "badges": [
            ("🟢 Speed Engine Online", "badge-success"),
            ("⚡ Calculation Tricks", "badge-primary"),
            ("🧩 Seating Arrangements", "badge-purple"),
            ("💳 Financial Awareness", "badge-amber")
        ]
    },
    "SSC": {
        "title": "SSC CGL & CHSL Prep Copilot",
        "subtitle": "Staff Selection Commission · Quant, Reasoning & General Awareness",
        "tag": "SSC CGL",
        "badges": [
            ("🟢 Tier 1 & 2 Core Online", "badge-success"),
            ("⚡ Speed Hacks Active", "badge-primary"),
            ("🏛️ Static GK Matrix", "badge-purple"),
            ("📝 Pattern Mocks Ready", "badge-amber")
        ]
    }
}


def render_minimal_topbar(selected_exam: str = "UPSC", persona: str = "Personal Mentor"):
    """Renders the top selector bar matching the screenshot with exam pill and persona pill."""
    st.markdown(f"""
    <div class="minimal-topbar">
        <div class="topbar-brand">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 22L12 8L17 17L20 12L25 22H4Z" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 8L15 13" stroke="#60A5FA" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <div>
                <div class="topbar-logo-title">UPSC AI</div>
                <div class="topbar-logo-sub">Learn · Plan · Grow</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 9999px; padding: 5px 14px; font-size: 0.8rem; font-weight: 600; color: #334155; display: flex; align-items: center; gap: 6px;">
                <span style="color: #6366F1;">✨</span> Powered by RAG <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#22C55E;"></span>
            </div>
            <div style="width: 34px; height: 34px; border-radius: 50%; background: #EEF2FF; border: 1.5px solid #C7D2FE; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #4338CA; font-size: 0.88rem;">
                K
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_exam_header(selected_exam: str = "UPSC"):
    """Clean minimal header for inner feature views."""
    config = EXAM_META_CONFIG.get(selected_exam, EXAM_META_CONFIG["UPSC"])
    badges_html = "".join([f'<span class="status-badge {b[1]}">{b[0]}</span>' for b in config["badges"]])
    
    st.markdown(f"""
    <div class="minimal-page-header">
        <div>
            <div class="minimal-page-title">{config['title']}</div>
            <div class="minimal-page-desc">{config['subtitle']}</div>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
            {badges_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_futuristic_header():
    render_exam_header("UPSC")
