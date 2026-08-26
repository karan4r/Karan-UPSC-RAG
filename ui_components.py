import streamlit as st
import json
from pathlib import Path

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Outfit:wght@600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Background - Deep Navy #0F172A */
    .stApp {
        background-color: #0F172A !important;
        background-image: none !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        color: #F8FAFC !important;
    }

    /* Secondary Text - Light Gray #CBD5E1 */
    html, body, p, span, div, li, label, td, th, .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #CBD5E1 !important;
    }

    /* Primary Text - Off White #F8FAFC */
    h1, h2, h3, h4, h5, h6, strong, b, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #F8FAFC !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }

    /* Accent Labels - Cyan #38BDF8 */
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

    /* Sidebar - Deep Navy #0F172A */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }

    /* Header Banner - Slate #1E293B */
    .futuristic-header {
        background-color: #1E293B !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 16px !important;
        padding: 26px 32px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .futuristic-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: #38BDF8 !important;
    }

    .header-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
        margin: 0 !important;
    }

    .header-subtitle {
        font-size: 0.95rem !important;
        color: #CBD5E1 !important;
        margin-top: 6px !important;
        font-weight: 500 !important;
    }

    /* Badges */
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
    }

    .badge-primary {
        background: rgba(56, 189, 248, 0.15) !important;
        color: #38BDF8 !important;
        border: 1px solid #38BDF8 !important;
    }

    .badge-success {
        background: rgba(52, 211, 153, 0.15) !important;
        color: #34D399 !important;
        border: 1px solid #34D399 !important;
    }

    .badge-purple {
        background: rgba(192, 132, 252, 0.15) !important;
        color: #C084FC !important;
        border: 1px solid #C084FC !important;
    }

    /* Surface Cards - Slate #1E293B */
    form[key="top_query_form"], form[key^="query_form_"], div[data-testid="stForm"] {
        background-color: #1E293B !important;
        border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 16px !important;
        padding: 22px 26px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 24px !important;
    }

    form[key^="query_form_"] input, div[data-testid="stForm"] input {
        border: 1.5px solid rgba(56, 189, 248, 0.4) !important;
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        font-size: 1.02rem !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        padding: 12px 18px !important;
    }

    form[key^="query_form_"] input:focus, div[data-testid="stForm"] input:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
    }

    /* Buttons - Cyan #38BDF8 Accent */
    .stButton>button {
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        border: 1px solid #38BDF8 !important;
        color: #FFFFFF !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(56, 189, 248, 0.5) !important;
        background: #0284C7 !important;
    }

    /* Radio Navigation Tabs */
    div[data-testid="stRadio"] > div,
    div[data-testid="stRadio"] [role="radiogroup"],
    div[data-testid="stWidgetGroup"] {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        background-color: #1E293B !important;
        padding: 8px !important;
        border-radius: 14px !important;
        border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
        width: 100% !important;
    }

    div[data-testid="stRadio"] label,
    div[role="radiogroup"] label {
        background-color: #0F172A !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #CBD5E1 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin: 2px !important;
        display: inline-flex !important;
        align-items: center !important;
    }

    div[data-testid="stRadio"] label:hover,
    div[role="radiogroup"] label:hover {
        color: #F8FAFC !important;
        border-color: #38BDF8 !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"],
    div[role="radiogroup"] label[aria-checked="true"],
    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #F8FAFC !important;
        border: 1px solid #38BDF8 !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.35) !important;
    }

    div[data-testid="stRadio"] label p,
    div[role="radiogroup"] label p,
    div[data-testid="stRadio"] label span,
    div[role="radiogroup"] label span {
        color: inherit !important;
        font-weight: inherit !important;
        font-size: 0.92rem !important;
    }

    /* Chat Messages */
    div[data-testid="stChatMessage"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        margin-bottom: 16px !important;
    }

    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li {
        color: #F8FAFC !important;
        font-size: 0.98rem !important;
        line-height: 1.65 !important;
    }

    div[data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background-color: #1E293B !important;
        border: 1.5px solid #38BDF8 !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 14px !important;
        margin-bottom: 16px !important;
    }

    div[data-testid="stExpander"] summary {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }

    /* Metric Cards - Slate #1E293B */
    .metric-card {
        background-color: #1E293B !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #38BDF8 !important;
    }

    .metric-label {
        font-size: 0.85rem !important;
        color: #CBD5E1 !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Surface Cards - Slate #1E293B */
    .pwskills-card {
        background-color: #1E293B !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        margin-bottom: 16px !important;
        transition: all 0.2s ease !important;
    }

    .pwskills-card:hover {
        border-color: #38BDF8 !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.25) !important;
    }

    .pwskills-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #38BDF8 !important;
    }

    .pwskills-desc {
        font-size: 0.95rem !important;
        color: #CBD5E1 !important;
        margin-top: 6px !important;
        line-height: 1.55 !important;
    }

    .pwskills-link {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        text-decoration: none !important;
    }

    .pwskills-link:hover {
        text-decoration: underline !important;
    }
    </style>
    """, unsafe_allow_html=True)

EXAM_META_CONFIG = {
    "UPSC": {
        "title": "⚡ UPSC AI NEURAL COPILOT",
        "subtitle": "Civil Services Examination (IAS / IPS / IFS) · Quantum RAG Neural Engine",
        "badges": [
            ("🟢 RAG NEURAL CORE: ONLINE", "badge-success"),
            ("🧠 623 MAINS MICROTOPICS ACTIVE", "badge-primary"),
            ("🧘 MENTAL HEALTH & WELLNESS: ACTIVE", "badge-purple"),
            ("📝 PRELIMS & MAINS MOCKS: READY", "badge-success")
        ]
    },
    "IIT-JEE": {
        "title": "⚛️ IIT-JEE AI NEURAL MENTOR",
        "subtitle": "Engineering Entrance (Physics, Chemistry & Mathematics) · Step-by-Step Problem Solving Engine",
        "badges": [
            ("🟢 JEE MAIN & ADVANCED CORE: ONLINE", "badge-success"),
            ("📐 FORMULAS & DERIVATIONS ACTIVE", "badge-primary"),
            ("💡 SHORTCUT & STEP-BY-STEP SOLVER", "badge-purple"),
            ("🎯 HIGH-YIELD JEE MOCKS: READY", "badge-success")
        ]
    },
    "NEET": {
        "title": "🩺 NEET UG MEDICAL COPILOT",
        "subtitle": "National Eligibility cum Entrance Test (NCERT Bio, Chem & Physics) · NCERT Line-by-Line Engine",
        "badges": [
            ("🟢 NCERT MASTER MATRIX: ONLINE", "badge-success"),
            ("🧬 BIOLOGY, CHEM & PHYSICS HIGH-YIELD", "badge-primary"),
            ("🔬 ASSERTION-REASON PRACTICE: ACTIVE", "badge-purple"),
            ("💡 MNEMONIC & RECALL ENGINE: READY", "badge-success")
        ]
    },
    "GATE": {
        "title": "⚙️ GATE ENGINEERING AI COPILOT",
        "subtitle": "Graduate Aptitude Test in Engineering (CS, EE, EC, ME, CE) · Numerical & Algorithmic Solver",
        "badges": [
            ("🟢 GATE TECHNICAL ENGINE: ONLINE", "badge-success"),
            ("📊 NUMERICAL ANSWER TYPE (NAT) READY", "badge-primary"),
            ("💻 CORE SUBJECT & ALGO MATRIX", "badge-purple"),
            ("⚡ STEP-BY-STEP DERIVATIONS: ACTIVE", "badge-success")
        ]
    },
    "CAT": {
        "title": "📈 CAT APTITUDE & DILR MASTER",
        "subtitle": "Common Admission Test for IIMs (QA, DILR, VARC) · Speed Math & Logical Breakdown Engine",
        "badges": [
            ("🟢 CAT STRATEGY MATRIX: ONLINE", "badge-success"),
            ("⚡ SPEED MATH & SHORTCUT ELIMINATION", "badge-primary"),
            ("🧩 DILR PUZZLE MATRIX ACTIVE", "badge-purple"),
            ("📚 VARC PASSAGE ANALYSIS: READY", "badge-success")
        ]
    },
    "Banking": {
        "title": "🏦 BANKING EXAM AI COPILOT",
        "subtitle": "IBPS PO/Clerk, SBI PO/Clerk & RBI Grade B · Speed Aptitude & Financial Awareness Engine",
        "badges": [
            ("🟢 BANKING SPEED ENGINE: ONLINE", "badge-success"),
            ("⚡ 30-SEC CALCULATION TRICKS", "badge-primary"),
            ("🧩 SYLLOGISM & SEATING ARRANGEMENT", "badge-purple"),
            ("💳 FINANCIAL AWARENESS: ACTIVE", "badge-success")
        ]
    },
    "SSC": {
        "title": "🏢 SSC CGL & CHSL PREP COPILOT",
        "subtitle": "Staff Selection Commission Tier-1 & Tier-2 · Quant, Reasoning, English & GA Speed Engine",
        "badges": [
            ("🟢 SSC TIER-1 & TIER-2 CORE: ONLINE", "badge-success"),
            ("⚡ SPEED HACKS & OPTION SUBSTITUTION", "badge-primary"),
            ("🏛️ STATIC GA MEMORY MATRIX", "badge-purple"),
            ("📝 PATTERN MOCKS & REASONING: READY", "badge-success")
        ]
    }
}

def render_exam_header(selected_exam: str = "UPSC"):
    config = EXAM_META_CONFIG.get(selected_exam, EXAM_META_CONFIG["UPSC"])
    badges_html = "".join([f'<span class="status-badge {b[1]}">{b[0]}</span>' for b in config["badges"]])
    
    st.markdown(f"""
    <div class="futuristic-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 class="header-title">{config['title']}</h1>
                <div class="header-subtitle">{config['subtitle']}</div>
            </div>
            <div style="text-align: right;">
                <span style="font-family:'JetBrains Mono'; font-size:0.78rem; background:rgba(56,189,248,0.15); color:#38BDF8; padding:5px 12px; border-radius:12px; border:1px solid rgba(56,189,248,0.3); font-weight:700;">
                    VERTICAL: {selected_exam}
                </span>
            </div>
        </div>
        <div class="status-badge-container">
            {badges_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_futuristic_header():
    render_exam_header("UPSC")

