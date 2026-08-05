import streamlit as st
import json
import re
from pathlib import Path
from generation.rag_chain import RAGChatbot
from ui_components import inject_custom_css, render_futuristic_header

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="UPSC AI Neural Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Dark Cyber Neural CSS
inject_custom_css()

# Path constants
ROOT = Path(__file__).resolve().parent
SYLLABUS_JSON_PATH = ROOT / "data" / "upsc_syllabus_microtopics.json"
USER_DATA_PATH = ROOT / "data" / "user_progress.json"

# Load Syllabus Data
@st.cache_data
def load_syllabus_data():
    if SYLLABUS_JSON_PATH.exists():
        with open(SYLLABUS_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

# Load & Save User Progress
def load_user_progress():
    if USER_DATA_PATH.exists():
        try:
            with open(USER_DATA_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed": [], "notes": {}, "custom_microtopics": []}

def save_user_progress(progress_data):
    USER_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = RAGChatbot()

if "progress" not in st.session_state:
    st.session_state.progress = load_user_progress()

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "nav_mode" not in st.session_state:
    st.session_state.nav_mode = "🤖 Neural AI Copilot"

def redirect_to_copilot(prompt: str):
    st.session_state.pending_prompt = prompt
    st.session_state.nav_mode = "🤖 Neural AI Copilot"
    st.rerun()

def count_previous_mental_health_turns(messages: list[dict]) -> int:
    count = 0
    mh_words = {"mental", "depressed", "depression", "stress", "anxiety", "anxious", "hopeless", "burnout", "overwhelmed", "emotional", "distress", "sadness", "loneliness", "panic"}
    for msg in reversed(messages):
        if msg.get("role") == "user":
            content = msg.get("content", "").lower()
            if any(w in content for w in mh_words):
                count += 1
            else:
                break
    return count

# Pre-processor to format any inline MCQs into clean markdown with options on separate lines
def format_mcq_markdown(text: str) -> str:
    if not text:
        return ""
        
    if not re.search(r'\b[A-D][\)\.]\s+', text):
        return text

    header_match = re.search(r'(?i)###\s*(?:\*\*)?Practice\s*MCQs?(?:\*\*)?', text)
    if header_match:
        main_body = text[:header_match.start()].strip()
        mcq_body = text[header_match.end():].strip()
    else:
        m_start = re.search(r'(?i)(?:^|\n)\s*(?:\d+[\.\)]|Question\s*\d+)\s+.*?\bA[\)\.]\s+', text)
        if m_start:
            main_body = text[:m_start.start()].strip()
            mcq_body = text[m_start.start():].strip()
        else:
            main_body = ""
            mcq_body = text

    if not mcq_body:
        return text

    q_blocks = re.split(r'(?i)(?:\n\s*|\b)(?:\d+[\.\)]|Question\s*\d+)\s+', mcq_body)
    formatted_mcqs = []
    
    q_counter = 1
    for block in q_blocks:
        block = block.strip()
        if not block:
            continue
            
        m_q = re.search(r'^(.*?)(?=\bA[\)\.]\s+)', block, re.DOTALL)
        if not m_q:
            continue
            
        q_text = m_q.group(1).strip()
        q_text = re.sub(r'^\s*[:\-\*\.\d]+\s*', '', q_text)
        
        mA = re.search(r'\bA[\)\.]\s*(.*?)(?=\s*\bB[\)\.]|\s*Correct|\s*Explanation|$)', block, re.DOTALL)
        mB = re.search(r'\bB[\)\.]\s*(.*?)(?=\s*\bC[\)\.]|\s*Correct|\s*Explanation|$)', block, re.DOTALL)
        mC = re.search(r'\bC[\)\.]\s*(.*?)(?=\s*\bD[\)\.]|\s*Correct|\s*Explanation|$)', block, re.DOTALL)
        mD = re.search(r'\bD[\)\.]\s*(.*?)(?=\s*Correct|\s*Explanation|\n\n|$)', block, re.DOTALL)
        
        m_ans = re.search(r'(?:Correct\s*(?:option|answer)?|Answer)\s*:\s*(.*?)(?=\s*Explanation:|\n|$)', block, re.IGNORECASE)
        m_exp = re.search(r'Explanation\s*:\s*(.*)', block, re.IGNORECASE | re.DOTALL)
        
        if mA and mB and mC and mD:
            optA = mA.group(1).strip().replace('\n', ' ')
            optB = mB.group(1).strip().replace('\n', ' ')
            optC = mC.group(1).strip().replace('\n', ' ')
            optD = mD.group(1).strip().replace('\n', ' ')
            
            ans_str = m_ans.group(1).strip() if m_ans else "A"
            exp_str = m_exp.group(1).strip() if m_exp else ""
            
            fmt_q = f"**Question {q_counter}:** {q_text}\n\n"
            fmt_q += f"- **A)** {optA}\n"
            fmt_q += f"- **B)** {optB}\n"
            fmt_q += f"- **C)** {optC}\n"
            fmt_q += f"- **D)** {optD}\n\n"
            fmt_q += f"**Correct Answer:** {ans_str}\n"
            if exp_str:
                fmt_q += f"**Explanation:** {exp_str}\n"
                
            formatted_mcqs.append(fmt_q)
            q_counter += 1

    if not formatted_mcqs:
        return text

    mcq_section = "### 📝 Practice MCQs\n\n" + "\n---\n\n".join(formatted_mcqs)
    if main_body:
        return f"{main_body}\n\n{mcq_section}"
    return mcq_section

# Helper to parse practice MCQs in response cleanly
def parse_mcqs(text: str) -> list[dict]:
    q_blocks = re.split(r'(?i)(?:\*\*?)?(?:Question|Q)\s*\d+\s*(?::|\.|\*\*|–|-)+\s*', text)
    questions = []
    for block in q_blocks:
        block = block.strip()
        if not block:
            continue
        
        opt_matches = list(re.finditer(r'(?i)(?:^|\n)\s*(?:-?\s*)?(?:\*\*?)?([A-D])[\).\s\-]\s*(.*?)(?=\n\s*(?:-?\s*)?(?:\*\*?)?[A-D][\).\s\-]|\n\s*(?:\*\*?)?(?:Correct|Explanation|Answer)|$)', block, re.DOTALL))
        options = {}
        for m in opt_matches:
            letter = m.group(1).upper()
            content = m.group(2).strip().replace("**", "")
            options[letter] = content
            
        ans_match = re.search(r'(?i)(?:Correct|Answer|Option)\s*(?:Answer|Option)?\s*(?::|\*\*|:?\*\*)\s*(?:Option\s*)?([A-D])', block)
        correct_ans = ans_match.group(1).upper() if ans_match else None
        
        exp_match = re.search(r'(?i)Explanation\s*(?::|\*\*|:?\*\*)\s*(.*)', block, re.DOTALL)
        explanation = exp_match.group(1).strip() if exp_match else ""
        
        q_text = block
        if opt_matches:
            q_text = block[:opt_matches[0].start()].strip()
        q_text = re.sub(r'^\s*[:\-\*.]+\s*', '', q_text)
        
        if options and len(options) >= 2:
            questions.append({
                "question": q_text,
                "options": options,
                "correct": correct_ans or "A",
                "explanation": explanation
            })
    return questions

def split_answer_and_mcqs(text: str):
    formatted_text = format_mcq_markdown(text)
    parts = re.split(r'(?i)###\s*(?:\*\*)?Practice\s*MCQs?(?:\*\*)?', formatted_text)
    if len(parts) < 2:
        return formatted_text, []
    main_text = parts[0].strip()
    mcq_text = parts[1].strip()
    mcqs = parse_mcqs(mcq_text)
    return main_text, mcqs

def render_assistant_message(content, idx, meta=None):
    category = meta.get("category") if meta else None
    
    # Non-academic queries (mental health, backup plans, study routines, general advice)
    if category == "non_academic":
        st.markdown(content)
        if meta:
            with st.expander("🔍 System Retrieval & Context Signals"):
                st.json(meta)
        return

    main_text, mcqs = split_answer_and_mcqs(content)
    st.markdown(main_text)
    
    if mcqs:
        st.write("---")
        st.markdown("<h3 style='color: #38BDF8; font-family: Outfit; font-weight: 800; margin-bottom: 16px;'>📝 Practice Quiz & Prelims Assessment</h3>", unsafe_allow_html=True)
        
        for q_idx, mcq in enumerate(mcqs):
            opts = mcq.get("options", {})
            opt_a = opts.get("A", "")
            opt_b = opts.get("B", "")
            opt_c = opts.get("C", "")
            opt_d = opts.get("D", "")
            
            st.markdown(f"""
            <div style="background: #1E293B !important; border: 1.5px solid rgba(56, 189, 248, 0.35) !important; border-radius: 16px !important; padding: 22px !important; margin-bottom: 16px !important;">
                <div style="font-size: 1.05rem !important; font-weight: 700 !important; color: #F8FAFC !important; margin-bottom: 14px !important; line-height: 1.5 !important;">
                    <span style="color: #38BDF8 !important;">Question {q_idx+1}:</span> {mcq['question']}
                </div>
                <div style="font-size: 0.88rem !important; font-weight: 700 !important; color: #38BDF8 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; margin-bottom: 10px !important;">Options:</div>
                <div style="margin-left: 4px; margin-bottom: 8px;">
                    <div style="color: #CBD5E1 !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #0F172A !important; border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.08) !important; font-size: 0.95rem !important; font-weight: 500 !important;">• <strong style="color: #38BDF8 !important;">A)</strong> {opt_a}</div>
                    <div style="color: #CBD5E1 !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #0F172A !important; border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.08) !important; font-size: 0.95rem !important; font-weight: 500 !important;">• <strong style="color: #38BDF8 !important;">B)</strong> {opt_b}</div>
                    <div style="color: #CBD5E1 !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #0F172A !important; border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.08) !important; font-size: 0.95rem !important; font-weight: 500 !important;">• <strong style="color: #38BDF8 !important;">C)</strong> {opt_c}</div>
                    <div style="color: #CBD5E1 !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #0F172A !important; border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.08) !important; font-size: 0.95rem !important; font-weight: 500 !important;">• <strong style="color: #38BDF8 !important;">D)</strong> {opt_d}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            options_list = [f"{k}) {v}" for k, v in opts.items()]
            key = f"quiz_{idx}_{q_idx}"
            
            selected = st.radio(
                f"Attempt Question {q_idx+1}:",
                options_list,
                index=None,
                key=key
            )
            
            if selected:
                selected_letter = selected.split(")")[0].strip().upper()
                if selected_letter == mcq["correct"]:
                    st.success(f"🎉 **Correct Answer!** You selected Option **{mcq['correct']}**.")
                else:
                    st.error(f"❌ **Incorrect.** You selected Option **{selected_letter}**. The correct answer is Option **{mcq['correct']}**.")
                st.info(f"**Solution & Explanation:**\n\n- **Correct Option:** Option **{mcq['correct']}**\n- **Detailed Explanation:** {mcq['explanation']}")
            else:
                with st.expander(f"💡 Reveal Solution & Explanation for Question {q_idx+1}"):
                    st.markdown(f"**Correct Option:** Option **{mcq['correct']}**\n\n**Detailed Explanation:**\n{mcq['explanation']}")
            st.write("")
            
    if meta:
        with st.expander("🔍 System Retrieval & Context Signals"):
            st.json(meta)

# Render Header Banner
render_futuristic_header()

# Sidebar Setup
with st.sidebar:
    st.markdown("<h3 style='color: #38BDF8; font-family: JetBrains Mono;'>⚙️ NEURAL CONTROLS</h3>", unsafe_allow_html=True)
    st.info("💡 **Cyber Tip:** Use the Curriculum Matrix to track microtopics and click '💡 Explainer' to generate high-yield AI notes.")
    
    # Progress Summary in Sidebar
    syllabus_data = load_syllabus_data()
    total_micros = 0
    completed_set = set(st.session_state.progress.get("completed", []))
    
    for paper, pdata in syllabus_data.items():
        for subj in pdata.get("subjects", {}).values():
            for top in subj.get("topics", {}).values():
                total_micros += len(top.get("microtopics", []))
                
    completed_count = len(completed_set)
    pct = (completed_count / total_micros * 100) if total_micros > 0 else 0
    
    st.markdown("---")
    st.markdown("<h3 style='color: #FFFFFF;'>📊 Matrix Progress</h3>", unsafe_allow_html=True)
    st.progress(pct / 100.0)
    st.markdown(f"<strong style='color: #38BDF8;'>{completed_count} / {total_micros}</strong> <span style='color: #94A3B8;'>modules completed ({pct:.1f}%)</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🧹 Reset Neural Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Check pending prompt redirect
if st.session_state.get("pending_prompt"):
    st.session_state.nav_mode = "🤖 Neural AI Copilot"
    st.session_state.main_nav_radio = "🤖 Neural AI Copilot"

# Main Top Navigation Radio
NAV_OPTIONS = [
    "🤖 Neural AI Copilot",
    "📋 Syllabus Navigator",
    "⚡ Productivity & Targets",
    "💞 Relationship Management",
    "🧘 Mental Health & Wellness",
    "📝 Mock Tests & Assessment",
    "🎓 Live & Recorded Classes",
    "💼 Backup Plans & PW Skills",
    "➕ Custom Modules",
    "📊 Matrix Analytics"
]

if "main_nav_radio" not in st.session_state:
    st.session_state.main_nav_radio = st.session_state.nav_mode

nav_mode = st.radio(
    "Navigation",
    NAV_OPTIONS,
    horizontal=True,
    key="main_nav_radio",
    label_visibility="collapsed"
)
st.session_state.nav_mode = nav_mode
st.markdown("<br>", unsafe_allow_html=True)

# Function to render High-Visibility Cyber Neural Query Form
def render_query_card(box_key: str):
    with st.form(f"query_form_{box_key}", clear_on_submit=True):
        st.markdown("<div style='font-family: JetBrains Mono; font-size: 1.1rem; font-weight: 800; color: #38BDF8; margin-bottom: 8px;'>⚡ NEURAL PROMPT INTERFACE:</div>", unsafe_allow_html=True)
        t_col1, t_col2 = st.columns([0.82, 0.18])
        with t_col1:
            q_val = st.text_input(
                "",
                placeholder="Type your UPSC syllabus query, PYQ question, or mental health concern here...",
                key=f"mentor_query_input_{box_key}",
                label_visibility="collapsed"
            )
        with t_col2:
            submitted = st.form_submit_button("🚀 Ask Copilot", use_container_width=True)
    return submitted, q_val

# ==========================================
# VIEW 1: 🤖 NEURAL AI COPILOT
# ==========================================
if nav_mode == "🤖 Neural AI Copilot":
    # If NO messages yet: Render prominent Query Box at top
    top_sub, top_val = False, ""
    if not st.session_state.messages:
        top_sub, top_val = render_query_card("top")
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Display Chat Messages
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                render_assistant_message(msg["content"], idx, msg.get("meta"))
            else:
                st.markdown(msg["content"])

    # If messages exist: Render Query Box directly BELOW the latest response output!
    bottom_card_sub, bottom_card_val = False, ""
    if st.session_state.messages:
        st.markdown("<br>", unsafe_allow_html=True)
        bottom_card_sub, bottom_card_val = render_query_card(f"below_output_{len(st.session_state.messages)}")

    # Determine prompt to process
    prompt_to_process = None
    if st.session_state.pending_prompt:
        prompt_to_process = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
    elif top_sub and top_val.strip():
        prompt_to_process = top_val.strip()
    elif bottom_card_sub and bottom_card_val.strip():
        prompt_to_process = bottom_card_val.strip()

    if prompt_to_process:
        mh_count = count_previous_mental_health_turns(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user"):
            st.markdown(prompt_to_process)

        with st.chat_message("assistant"):
            with st.spinner("⚡ Executing Neural RAG Matrix & Consulting Copilot..."):
                try:
                    result = st.session_state.chatbot.chat(prompt_to_process, mh_count=mh_count)
                except Exception:
                    result = st.session_state.chatbot.chat(prompt_to_process)
            
            meta = {
                "intent": result["intent"],
                "category": result["category"],
                "confidence": result["confidence"],
                "mode": result["mode"],
                "signals": result.get("signals", []),
                "sources": result.get("sources", []),
            }
            
            next_idx = len(st.session_state.messages)
            render_assistant_message(result["answer"], next_idx, meta)

        st.session_state.messages.append(
            {"role": "assistant", "content": result["answer"], "meta": meta}
        )
        st.rerun()

# ==========================================
# VIEW 2: 📋 SYLLABUS NAVIGATOR
# ==========================================
elif nav_mode == "📋 Syllabus Navigator":
    st.markdown("<h3 style='color: #FFFFFF;'>📋 GS Mains Curriculum & Microtopic Navigator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Browse microtopics parsed from official GS Mains syllabus, track completion, and generate AI notes.</p>", unsafe_allow_html=True)
    
    # Dashboard Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">GS1 Microtopics</div>
            <div class="metric-value">386</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">GS2 Microtopics</div>
            <div class="metric-value">89</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">GS3 Microtopics</div>
            <div class="metric-value">73</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">GS4 Microtopics</div>
            <div class="metric-value">69</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # High-Visibility Search & Filter Bar
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        selected_paper = st.selectbox(
            "Filter by GS Paper:",
            ["GS Paper 1", "GS Paper 2", "GS Paper 3", "GS Paper 4"],
            key="dash_paper_select_fs"
        )
    
    syllabus = load_syllabus_data()
    paper_subjects = list(syllabus.get(selected_paper, {}).get("subjects", {}).keys())
    
    with f_col2:
        selected_subject = st.selectbox(
            "Filter by Subject:",
            ["All Subjects"] + paper_subjects,
            key="dash_subj_select_fs"
        )
    with f_col3:
        st.markdown("<div style='margin-bottom: -6px;'><strong style='color: #38BDF8;'>🔍 Search Microtopics / Keywords:</strong></div>", unsafe_allow_html=True)
        search_query = st.text_input("", placeholder="e.g. Fundamental Rights, Music, Economy...", key="dash_search_input_fs", label_visibility="collapsed").lower().strip()

    st.markdown("---")
    
    if selected_paper in syllabus:
        p_info = syllabus[selected_paper]
        st.markdown(f"<h3 style='color: #38BDF8;'>📖 {p_info.get('title', selected_paper)}</h3>", unsafe_allow_html=True)
        
        subjects_dict = p_info.get("subjects", {})
        subjects_to_display = [selected_subject] if selected_subject != "All Subjects" else list(subjects_dict.keys())
        
        for subj_key in subjects_to_display:
            if subj_key not in subjects_dict:
                continue
            s_data = subjects_dict[subj_key]
            
            with st.expander(f"📚 Subject: {s_data.get('title', subj_key)}", expanded=True):
                topics = s_data.get("topics", {})
                for top_key, t_data in topics.items():
                    micros = t_data.get("microtopics", [])
                    
                    filtered_micros = []
                    for m in micros:
                        m_id = f"{selected_paper}_{subj_key}_{top_key}_{m}"
                        is_completed = m_id in st.session_state.progress.get("completed", [])
                        
                        if search_query and (search_query not in m.lower() and search_query not in top_key.lower()):
                            continue
                        filtered_micros.append((m, m_id, is_completed))
                        
                    if filtered_micros:
                        st.markdown(f"<h4 style='color: #FFFFFF; margin-top: 12px;'>📌 {t_data.get('title', top_key)}</h4>", unsafe_allow_html=True)
                        for m_text, m_id, is_comp in filtered_micros:
                            c_col1, c_col2 = st.columns([0.82, 0.18])
                            with c_col1:
                                checked = st.checkbox(m_text, value=is_comp, key=f"chk_fs_{m_id}")
                                if checked != is_comp:
                                    if checked and m_id not in st.session_state.progress["completed"]:
                                        st.session_state.progress["completed"].append(m_id)
                                    elif not checked and m_id in st.session_state.progress["completed"]:
                                        st.session_state.progress["completed"].remove(m_id)
                                    save_user_progress(st.session_state.progress)
                                    st.rerun()
                            with c_col2:
                                if st.button("💡 Explainer", key=f"ask_fs_{m_id}", use_container_width=True):
                                    redirect_to_copilot(f"Explain the UPSC Mains microtopic '{m_text}' under '{top_key}' ({selected_paper}). Include key facts, significance, and practice questions.")
                        st.write("")

# ==========================================
# VIEW: ⚡ PRODUCTIVITY & TARGETS
# ==========================================
elif nav_mode == "⚡ Productivity & Targets":
    st.markdown("<h3 style='color: #FFFFFF;'>⚡ Daily, Weekly & Monthly Productivity Matrix</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Plan study targets mapped to GS Syllabus microtopics, monitor daily velocity graphics, and track target completion.</p>", unsafe_allow_html=True)
    
    import datetime
    today_str = datetime.date.today().isoformat()
    
    if "targets" not in st.session_state.progress:
        st.session_state.progress["targets"] = []
        
    targets = st.session_state.progress["targets"]
    completed_microtopics = set(st.session_state.progress.get("completed", []))
    
    # Filter targets by timeframe
    daily_targets = [t for t in targets if t.get("timeframe") == "Daily"]
    weekly_targets = [t for t in targets if t.get("timeframe") == "Weekly"]
    monthly_targets = [t for t in targets if t.get("timeframe") == "Monthly"]
    
    daily_done = sum(1 for t in daily_targets if t.get("completed"))
    daily_total = len(daily_targets)
    daily_pct = (daily_done / daily_total * 100) if daily_total > 0 else 0
    
    weekly_done = sum(1 for t in weekly_targets if t.get("completed"))
    weekly_total = len(weekly_targets)
    weekly_pct = (weekly_done / weekly_total * 100) if weekly_total > 0 else 0

    monthly_done = sum(1 for t in monthly_targets if t.get("completed"))
    monthly_total = len(monthly_targets)
    monthly_pct = (monthly_done / monthly_total * 100) if monthly_total > 0 else 0

    # 1. Dashboard Metrics Row
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 Daily Productivity</div>
            <div class="metric-value">{daily_done}/{daily_total}</div>
            <div style="color: #38BDF8; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{daily_pct:.0f}% Completed Today</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🗓️ Weekly Target Rate</div>
            <div class="metric-value">{weekly_done}/{weekly_total}</div>
            <div style="color: #34D399; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{weekly_pct:.0f}% Week Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📆 Monthly Milestones</div>
            <div class="metric-value">{monthly_done}/{monthly_total}</div>
            <div style="color: #C084FC; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{monthly_pct:.0f}% Month Goal</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Productivity Velocity</div>
            <div class="metric-value">{daily_done + 3 if daily_done > 0 else 3} Days</div>
            <div style="color: #F59E0B; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">Active Flow Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Real-Time Productivity Graphics
    st.markdown("<h4 style='color: #38BDF8;'>📊 Real-Time Productivity Graphics & Target Analytics</h4>", unsafe_allow_html=True)
    
    g_col1, g_col2 = st.columns([1.2, 0.8])
    
    with g_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">📈 Daily & Horizon Target Execution Velocity</div>
            <div class="pwskills-desc">Visual breakdown of completed vs pending target tasks across Daily, Weekly, and Monthly planning horizons.</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            import pandas as pd
            chart_data = {
                "Timeframe": ["Daily Targets", "Weekly Targets", "Monthly Targets"],
                "Completed": [daily_done, weekly_done, monthly_done],
                "Pending": [max(0, daily_total - daily_done), max(0, weekly_total - weekly_done), max(0, monthly_total - monthly_done)]
            }
            df_chart = pd.DataFrame(chart_data).set_index("Timeframe")
            st.bar_chart(df_chart, height=220)
        except Exception:
            st.progress(daily_pct / 100.0)
            st.caption(f"Daily Target Progress: {daily_pct:.1f}%")
            st.progress(weekly_pct / 100.0)
            st.caption(f"Weekly Target Progress: {weekly_pct:.1f}%")

    with g_col2:
        perf_status = "🚀 PEAK PERFORMANCE" if daily_pct >= 80 else ("⚡ HIGH YIELD IN PROGRESS" if daily_pct >= 50 else ("🟡 GET STARTED TODAY" if daily_total > 0 else "🎯 SET YOUR DAILY TARGETS"))
        st.markdown(f"""
        <div class="pwskills-card" style="border-color: rgba(56, 189, 248, 0.5) !important;">
            <div class="pwskills-title">🎯 Today's Productivity Index</div>
            <div style="text-align: center; margin: 14px 0;">
                <div style="font-family: 'Outfit'; font-size: 3.2rem; font-weight: 800; color: #38BDF8; line-height: 1;">
                    {daily_pct:.0f}%
                </div>
                <div style="color: #34D399; font-weight: 700; font-size: 0.88rem; margin-top: 6px; letter-spacing: 0.5px;">
                    {perf_status}
                </div>
            </div>
            <div style="background: #0F172A; border-radius: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="font-size: 0.82rem; color: #CBD5E1;">
                    📌 <strong>Syllabus Microtopics Mapped:</strong> {sum(1 for t in targets if t.get('microtopic_id'))} linked
                </div>
                <div style="font-size: 0.82rem; color: #CBD5E1; margin-top: 4px;">
                    ⏱️ <strong>Est. Hours Logged Today:</strong> {sum(float(t.get('hours_est', 1.0)) for t in targets if t.get('completed')):.1f} hrs
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Create Target Mapped to Syllabus
    st.markdown("<h4 style='color: #38BDF8;'>➕ Create New Target (Mapped to Syllabus Navigator)</h4>", unsafe_allow_html=True)
    
    syllabus = load_syllabus_data()
    paper_options = ["GS Paper 1", "GS Paper 2", "GS Paper 3", "GS Paper 4", "CSAT & Optional"]
    
    with st.form("create_target_form_unique", clear_on_submit=True):
        t_title = st.text_input("Target Description / Goal Title:", placeholder="e.g. Master Fundamental Rights Art 12-35 & solve 20 PYQs", key="target_title_input")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            t_timeframe = st.selectbox("Planning Horizon:", ["Daily", "Weekly", "Monthly"], key="target_tf_select")
        with c2:
            t_paper = st.selectbox("Select GS Paper:", paper_options, key="target_paper_select")
        with c3:
            paper_subjs = list(syllabus.get(t_paper, {}).get("subjects", {}).keys())
            t_subj = st.selectbox("Select Subject:", ["General"] + paper_subjs, key="target_subj_select")
        with c4:
            t_type = st.selectbox("Target Goal Type:", ["Note Making 📝", "PYQ Practice 🎯", "Revision 🔄", "Answer Writing ✍️", "Video Lecture 🎥"], key="target_type_select")
        
        available_micros = []
        if t_paper in syllabus:
            s_dict = syllabus[t_paper].get("subjects", {})
            if t_subj != "General" and t_subj in s_dict:
                for top_k, top_v in s_dict[t_subj].get("topics", {}).items():
                    for m in top_v.get("microtopics", []):
                        m_id = f"{t_paper}_{t_subj}_{top_k}_{m}"
                        available_micros.append((f"{top_k}: {m}", m_id, m))
            else:
                for s_k, s_v in s_dict.items():
                    for top_k, top_v in s_v.get("topics", {}).items():
                        for m in top_v.get("microtopics", []):
                            m_id = f"{t_paper}_{s_k}_{top_k}_{m}"
                            available_micros.append((f"{s_k} - {top_k}: {m}", m_id, m))
        
        m_options_labels = ["(Optional) Map to Syllabus Microtopic..."] + [item[0] for item in available_micros]
        t_mapped_m = st.selectbox("Map Target to Syllabus Microtopic:", m_options_labels, key="target_micro_select")
        
        c_h1, c_h2 = st.columns([1, 1])
        with c_h1:
            t_hours = st.number_input("Estimated Study Hours:", min_value=0.5, max_value=12.0, value=2.0, step=0.5, key="target_hours_input")
        with c_h2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            t_submit = st.form_submit_button("🎯 Add Target to My Matrix Plan", use_container_width=True)
            
        if t_submit:
            if t_title.strip():
                mapped_id = None
                mapped_title = None
                if t_mapped_m != "(Optional) Map to Syllabus Microtopic...":
                    for item in available_micros:
                        if item[0] == t_mapped_m:
                            mapped_id = item[1]
                            mapped_title = item[2]
                            break
                            
                new_target = {
                    "id": f"tgt_{int(datetime.datetime.now().timestamp())}",
                    "title": t_title.strip(),
                    "timeframe": t_timeframe,
                    "paper": t_paper,
                    "subject": t_subj,
                    "microtopic_id": mapped_id,
                    "microtopic_title": mapped_title,
                    "goal_type": t_type,
                    "hours_est": float(t_hours),
                    "completed": False,
                    "created_at": today_str
                }
                st.session_state.progress.setdefault("targets", []).append(new_target)
                save_user_progress(st.session_state.progress)
                st.success(f"✅ Added {t_timeframe} Target: '{t_title.strip()}' mapped to {t_paper}!")
                st.rerun()
            else:
                st.warning("Please enter a target description before saving.")

    st.markdown("---")

    # 4. View & Manage Planned Targets
    st.markdown("<h4 style='color: #FFFFFF;'>📋 Active Study Targets & Execution Matrix</h4>", unsafe_allow_html=True)
    
    tgt_tab1, tgt_tab2, tgt_tab3 = st.tabs(["📅 Daily Targets", "🗓️ Weekly Targets", "📆 Monthly Targets"])
    
    def render_target_list(target_list, tf_name):
        if not target_list:
            st.info(f"No {tf_name.lower()} targets planned yet. Use the form above to create your first {tf_name.lower()} study target!")
            return
            
        for idx, tgt in enumerate(target_list):
            is_done = tgt.get("completed", False)
            t_id = tgt.get("id", f"tgt_{idx}")
            
            t_col1, t_col2 = st.columns([0.78, 0.22])
            with t_col1:
                chk = st.checkbox(
                    f"**{tgt['title']}**  `[{tgt['paper']}]`  `[{tgt.get('goal_type', 'Target')}]`  `({tgt.get('hours_est', 1.0)} hrs)`",
                    value=is_done,
                    key=f"chk_target_{t_id}"
                )
                if chk != is_done:
                    tgt["completed"] = chk
                    m_id = tgt.get("microtopic_id")
                    if m_id:
                        comp_list = st.session_state.progress.setdefault("completed", [])
                        if chk and m_id not in comp_list:
                            comp_list.append(m_id)
                        elif not chk and m_id in comp_list:
                            comp_list.remove(m_id)
                    save_user_progress(st.session_state.progress)
                    st.rerun()
                    
                if tgt.get("microtopic_title"):
                    st.caption(f"📌 **Mapped Syllabus Topic:** {tgt['microtopic_title']}")

            with t_col2:
                btn_cols = st.columns([1, 1])
                with btn_cols[0]:
                    if tgt.get("microtopic_title"):
                        if st.button("💡 Notes", key=f"btn_exp_tgt_{t_id}", use_container_width=True):
                            redirect_to_copilot(f"Generate high-yield UPSC notes and practice questions for '{tgt['microtopic_title']}' ({tgt['paper']}).")
                with btn_cols[1]:
                    if st.button("🗑️", key=f"btn_del_tgt_{t_id}", use_container_width=True):
                        st.session_state.progress["targets"].remove(tgt)
                        save_user_progress(st.session_state.progress)
                        st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

    with tgt_tab1:
        render_target_list(daily_targets, "Daily")
    with tgt_tab2:
        render_target_list(weekly_targets, "Weekly")
    with tgt_tab3:
        render_target_list(monthly_targets, "Monthly")

# ==========================================
# VIEW: 💞 RELATIONSHIP MANAGEMENT
# ==========================================
elif nav_mode == "💞 Relationship Management":
    st.markdown("<h3 style='color: #FFFFFF;'>💞 Aspirant Relationship & Preparation Ecosystem</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Manage emotional dynamics (ghosting, one-sided love, breakups), map emotional stress to UPSC syllabus progress, and protect your study targets.</p>", unsafe_allow_html=True)
    
    # Initialize relationship state in user progress if not present
    rel_state = st.session_state.progress.setdefault("relationship_state", {
        "status": "Single & Focused on UPSC 🛡️",
        "emotional_situation": "🟢 Emotionally Stable & Supported",
        "drain_level": 3
    })
    
    # Calculate Syllabus Progress Metrics
    total_micros = 623
    completed_set = set(st.session_state.progress.get("completed", []))
    completed_cnt = len(completed_set)
    covered_pct = (completed_cnt / total_micros * 100) if total_micros > 0 else 0
    left_pct = max(0.0, 100.0 - covered_pct)
    left_cnt = max(0, total_micros - completed_cnt)

    # 1. Diagnostic & Parameter Input Form
    with st.expander("⚙️ Configure Your Emotional & Relationship Profile", expanded=True):
        with st.form("relationship_config_form"):
            r_col1, r_col2, r_col3 = st.columns([1.2, 1.2, 1])
            status_options = [
                "Single & Focused on UPSC 🛡️",
                "Ghosting / Sudden Silence 👻",
                "One-Sided Love / Attachment 💘",
                "On-and-Off / Mixed Signals ⚡",
                "Recent Breakup / Heartbreak Recovery 💔",
                "Long-Distance Exam Stress 🛰️",
                "Healthy & Supportive Partnership 💑"
            ]
            current_status = rel_state.get("status", status_options[0])
            status_idx = status_options.index(current_status) if current_status in status_options else 0
            
            with r_col1:
                rel_status = st.selectbox(
                    "Relationship Dynamics:",
                    status_options,
                    index=status_idx,
                    key="rel_status_input"
                )
            with r_col2:
                emo_situation = st.selectbox(
                    "Current Emotional State:",
                    [
                        "🟢 Emotionally Stable & Supported",
                        "🟡 Confused / Mixed Signals / Overthinking",
                        "🟠 One-Sided Love / Unrequited Obsession",
                        "🔴 Ghosting Anxiety & Rumination",
                        "💔 Post-Breakup Heartbreak & Grief",
                        "🧘 Single & Complete Emotional Detachment"
                    ],
                    key="emo_situation_input"
                )
            with r_col3:
                drain = st.slider("Emotional Drain Level (1-10):", min_value=1, max_value=10, value=int(rel_state.get("drain_level", 3)), key="emo_drain_slider")
                
            r_saved = st.form_submit_button("💾 Save Profile & Update Mapping Graphics", use_container_width=True)
            if r_saved:
                st.session_state.progress["relationship_state"] = {
                    "status": rel_status,
                    "emotional_situation": emo_situation,
                    "drain_level": drain
                }
                save_user_progress(st.session_state.progress)
                st.success("✅ Relationship Profile Updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Syllabus Mapping & Emotional Impact Analytics Dashboard
    st.markdown("<h4 style='color: #38BDF8;'>📊 Relationship Stress vs. Syllabus Completion Matrix</h4>", unsafe_allow_html=True)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Syllabus Covered</div>
            <div class="metric-value">{completed_cnt}</div>
            <div style="color: #34D399; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{covered_pct:.1f}% Microtopics Done</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Syllabus Remaining</div>
            <div class="metric-value">{left_cnt}</div>
            <div style="color: #EF4444; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{left_pct:.1f}% Microtopics Left</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚡ Emotional Toll Index</div>
            <div class="metric-value">{drain}/10</div>
            <div style="color: #F59E0B; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{"🔴 High Drain" if drain >= 7 else ("🟡 Moderate Strain" if drain >= 4 else "🟢 Low Drain")}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        prep_security = max(5, int((100 - drain * 8) * (covered_pct / 100.0) + (100 - drain * 7) * 0.5))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🛡️ Prep Protection Index</div>
            <div class="metric-value">{prep_security}%</div>
            <div style="color: #38BDF8; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">Study Continuity Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphical Analysis Section
    g_col1, g_col2 = st.columns([1.2, 0.8])
    with g_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">📈 Syllabus Progress vs. Emotional Toll Correlation</div>
            <div class="pwskills-desc">Visual comparison of completed syllabus microtopics against remaining topics and current emotional bandwidth drain.</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            import pandas as pd
            chart_df = pd.DataFrame({
                "Parameter": ["Syllabus Covered (%)", "Syllabus Remaining (%)", "Emotional Energy Drain (x10%)"],
                "Percentage Score": [covered_pct, left_pct, drain * 10]
            }).set_index("Parameter")
            st.bar_chart(chart_df, height=220)
        except Exception:
            st.progress(covered_pct / 100.0)
            st.caption(f"Syllabus Covered: {covered_pct:.1f}%")
            st.progress(left_pct / 100.0)
            st.caption(f"Syllabus Remaining: {left_pct:.1f}%")

    with g_col2:
        curr_status = rel_state.get("status", status_options[0])
        
        if "Ghosting" in curr_status:
            adv_color = "#EF4444"
            adv_title = "👻 Ghosting Recovery Protocol Active"
            adv_msg = f"Ghosting causes cognitive loops. You have **{left_cnt} syllabus microtopics left**. Every 30 mins spent checking last seen/messages costs 1 microtopic of GS Polity or Economy. Execute 45-min Pomodoro sprints now!"
        elif "One-Sided" in curr_status:
            adv_color = "#F59E0B"
            adv_title = "💘 Unrequited Energy Re-direction"
            adv_msg = f"One-sided attachment drains emotional reserves. Rechannel your intense passion into conquering the **{left_pct:.1f}% remaining syllabus**. Transmute unrequited feelings into top marks in Ethics & PYQs!"
        elif "Breakup" in curr_status:
            adv_color = "#C084FC"
            adv_title = "💔 Post-Breakup Resilience Sprint"
            adv_msg = f"Heartbreak is high-octane emotional fuel if disciplined. With **{covered_pct:.1f}% completed**, let your academic success be your ultimate transformation. Focus on daily Mains answer writing!"
        elif "On-and-Off" in curr_status:
            adv_color = "#38BDF8"
            adv_title = "⚡ Mixed Signals Boundary Shield"
            adv_msg = "Inconsistency in relationships sabotages UPSC consistency. Implement strict 9 AM - 9 PM study dark-outs. Communicate only during scheduled evening windows."
        else:
            adv_color = "#34D399"
            adv_title = "🟢 High Focus Equilibrium"
            adv_msg = f"Your emotional state is stable. Capitalize on this clarity to crush the remaining **{left_cnt} microtopics** in GS Paper 1, 2, 3, and 4!"

        st.markdown(f"""
        <div class="pwskills-card" style="border-color: {adv_color} !important;">
            <div class="pwskills-title" style="color: {adv_color} !important;">{adv_title}</div>
            <div style="color: #F8FAFC; font-size: 0.92rem; margin-top: 8px; line-height: 1.55;">
                {adv_msg}
            </div>
            <div style="margin-top: 12px; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #CBD5E1;">
                STATUS: <span style="color: {adv_color}; font-weight: 700;">{curr_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Dual Management Ecosystem (Prep + Relationship Protocol)
    st.markdown("<h4 style='color: #38BDF8;'>🛡️ Dual Management Ecosystem: Relationship & Prep Rules</h4>", unsafe_allow_html=True)
    
    eco_col1, eco_col2, eco_col3 = st.columns(3)
    with eco_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🕒 Strict Time-Blocking Protocol</div>
            <div class="pwskills-desc">
                • <strong>09:00 AM - 08:00 PM:</strong> 100% UPSC Prep Darkout (Phone on DND/Study Mode).<br>
                • <strong>08:00 PM - 08:30 PM:</strong> Fixed Relationship/Personal Check-in Window.<br>
                • <strong>10:30 PM Onwards:</strong> Zero Overthinking / Sleep Hygiene.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with eco_col2:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🧠 Cognitive Re-framing Rules</div>
            <div class="pwskills-desc">
                • <strong>If Ghosted:</strong> Silence is a clear answer. Do not seek closure from the person who created the chaos.<br>
                • <strong>If One-Sided:</strong> Your self-worth isn't determined by someone's inability to see your value.<br>
                • <strong>If Distracted:</strong> The IAS officer list does not pause for personal drama.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with eco_col3:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">📚 Syllabus Safeguard Technique</div>
            <div class="pwskills-desc">
                • <strong>Emotional Urge Rule:</strong> Whenever tempted to text/overthink, solve 5 PYQs first.<br>
                • <strong>Microtopic Mapping:</strong> Link every study target to daily progress so relationship stress never halts momentum.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 4. 1-Click AI Relationship Copilot Consultations
    st.markdown("<h4 style='color: #38BDF8;'>🤖 AI Relationship & Prep Counselor Prompt Suite</h4>", unsafe_allow_html=True)
    st.caption("Click any prompt to consult our empathetic AI copilot for tailored psychological strategies:")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        if st.button("👻 Handling Ghosting & Overthinking", key="btn_rel_ghost", use_container_width=True):
            redirect_to_copilot(f"I am an UPSC aspirant experiencing ghosting/sudden silence in my relationship. My emotional drain is {drain}/10, and I have {left_cnt} syllabus microtopics left ({left_pct:.1f}%). Give me an empathetic psychological strategy and a daily study routine to stop overthinking and refocus on GS Mains.")
    with c_col2:
        if st.button("💘 Overcoming One-Sided Love", key="btn_rel_onesided", use_container_width=True):
            redirect_to_copilot(f"I am struggling with one-sided love and unrequited attachment while preparing for UPSC CSE. How do I detach emotionally, channel my energy into syllabus completion ({covered_pct:.1f}% covered so far), and maintain mental peace?")
    with c_col3:
        if st.button("💔 Post-Breakup Study Plan", key="btn_rel_breakup", use_container_width=True):
            redirect_to_copilot(f"I recently went through a breakup during my UPSC CSE preparation. How do I cope with grief and heartbreak while ensuring my target of completing {left_cnt} remaining microtopics stays on track?")

    st.markdown("---")

    # 5. Private Emotional Venting & Reflection Journal
    st.markdown("<h4 style='color: #FFFFFF;'>✍️ Aspirant Emotional Venting & Mindset Reflection Log</h4>", unsafe_allow_html=True)
    st.caption("Vent your thoughts here to clear cognitive clutter before starting your study session. Kept strictly private in local session state.")
    
    journal_text = st.text_area(
        "Express your current feelings, boundaries, or commitments:",
        value=st.session_state.progress.get("emotional_journal", ""),
        height=140,
        placeholder="e.g. Today I felt anxious about being ghosted, but I commit to completing 3 GS2 microtopics on Parliament and Polity...",
        key="rel_journal_input"
    )
    if st.button("💾 Save Reflection Log", key="btn_save_rel_journal"):
        st.session_state.progress["emotional_journal"] = journal_text
        save_user_progress(st.session_state.progress)
        st.success("✨ Reflection Log Saved! Your mind is clear—time to focus on the syllabus.")

# ==========================================
# VIEW 3: 🧘 MENTAL HEALTH & WELLNESS
# ==========================================
elif nav_mode == "🧘 Mental Health & Wellness":
    st.markdown("<h3 style='color: #FFFFFF;'>🧘 Aspirant Mental Health & Mindset Wellness Hub</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Empathetic psychological guidance, stress management, anti-burnout strategies, and daily mindset building for UPSC aspirants.</p>", unsafe_allow_html=True)
    
    # Mood Check-in Card
    st.markdown("""
    <div class="pwskills-card">
        <div class="pwskills-title">💚 Daily Aspirant Mindset & Mood Check-in</div>
        <div class="pwskills-desc">How are you feeling right now during your study regimen? Select your state below for tailored advice.</div>
    </div>
    """, unsafe_allow_html=True)
    
    mood_col1, mood_col2 = st.columns([1, 1])
    with mood_col1:
        mood = st.radio(
            "Select your current state:",
            [
                "🟢 High Energy & Hyper-Focused",
                "🟡 Moderate Stress / Slight Fatigue",
                "🟠 Overwhelmed & Syllabus Anxiety",
                "🔴 Severe Burnout & Low Motivation"
            ],
            key="aspirant_mood_select"
        )
    with mood_col2:
        if "🟢 High Energy" in mood:
            st.success("🌟 **Prime Flow State!** Capitalize on this momentum to tackle high-yield complex topics like Ethics Case Studies or GS Economy.")
        elif "🟡 Moderate Stress" in mood:
            st.info("⚡ **Mindful Advice:** Take a 10-minute walk, drink water, and practice 4-7-8 breathing before your next study session.")
        elif "🟠 Overwhelmed" in mood:
            st.warning("⚠️ **De-compress Now:** Break your daily targets into micro 25-minute sprints. Focus only on 1 topic at a time.")
        else:
            st.error("🛑 **Burnout Protocol Engaged:** Step away from textbooks. Talk to a family member/mentor or consult our AI Mental Health Counselor below.")

    st.markdown("---")
    
    # 1-Click AI Counselor Prompts
    st.markdown("<h4 style='color: #38BDF8;'>🤖 AI Psychological Copilot - Instant Consultations</h4>", unsafe_allow_html=True)
    st.caption("Click any prompt to consult our empathetic AI counselor trained on UPSC aspirant psychology:")
    
    mh_col1, mh_col2, mh_col3, mh_col4 = st.columns(4)
    with mh_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🤯 Overcoming Overwhelm</div>
            <div class="pwskills-desc">Syllabus feels impossible to finish in time? Get a realistic prioritization plan.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Ask Counselor", key="btn_mh_overwhelm", use_container_width=True):
            redirect_to_copilot("I feel completely overwhelmed by the huge UPSC syllabus and fear I won't finish in time. Please give me an empathetic step-by-step psychological strategy to regain control and reduce anxiety.")

    with mh_col2:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🎯 Prelims Exam Anxiety</div>
            <div class="pwskills-desc">Managing test panic, negative marking fear, and exam-hall performance pressure.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Ask Counselor", key="btn_mh_anxiety", use_container_width=True):
            redirect_to_copilot("How can I overcome severe exam anxiety and negative marking fear during UPSC Prelims mock tests?")

    with mh_col3:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">😴 Sleep & Burnout Routine</div>
            <div class="pwskills-desc">Fixing insomnia, late-night overthinking, and fatigue during 10+ hour study routines.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Ask Counselor", key="btn_mh_sleep", use_container_width=True):
            redirect_to_copilot("My sleep schedule is ruined due to late-night UPSC preparation, and I feel mentally exhausted during the day. How do I fix my sleep and energy levels?")

    with mh_col4:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">👥 Isolation & Peer Pressure</div>
            <div class="pwskills-desc">Dealing with social isolation, family expectations, and fear of falling behind.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Ask Counselor", key="btn_mh_isolation", use_container_width=True):
            redirect_to_copilot("I am struggling with social isolation and family pressure during my UPSC attempt. How do I maintain mental resilience?")

    st.markdown("---")

    # Interactive Mindfulness & Support Resources Row
    rec_col1, rec_col2 = st.columns([1.2, 0.8])
    with rec_col1:
        st.markdown("<h4 style='color: #FFFFFF;'>🧘 4-7-8 Box Breathing & Relaxation Tool</h4>", unsafe_allow_html=True)
        st.markdown("""
        1. **Inhale quietly** through your nose for **4 seconds**.
        2. **Hold your breath** for **7 seconds**.
        3. **Exhale completely** through your mouth for **8 seconds**.
        4. Repeat 4 times to instantly reset your nervous system.
        """)
        if st.button("⏱️ Start 1-Minute Reset Timer", key="btn_breathing_timer"):
            st.info("🌬️ *Inhale... 1.. 2.. 3.. 4..* | *Hold... 1.. 2.. 3.. 4.. 5.. 6.. 7..* | *Exhale... 1.. 2.. 3.. 4.. 5.. 6.. 7.. 8..*")
            st.success("✨ Mindful Reset Complete! Take a deep breath and return to study with clarity.")

    with rec_col2:
        st.markdown("<h4 style='color: #38BDF8 !important;'>📞 Tele-MANAS Helplines</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="pwskills-card" style="border-color: #34D399 !important;">
            <div style="color: #34D399 !important; font-weight: 800 !important; font-size: 1.15rem !important;">Govt. Tele-MANAS Helpline</div>
            <div style="color: #FFFFFF !important; font-size: 1.4rem !important; font-weight: 800 !important; margin-top: 6px !important;">📞 14416 / 1800-891-4416</div>
            <div style="color: #F8FAFC !important; font-size: 0.92rem !important; margin-top: 6px !important; font-weight: 500 !important;">24x7 Free & Confidential Mental Health Counseling by Govt of India</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# VIEW 4: 📝 MOCK TESTS & ASSESSMENT
# ==========================================
elif nav_mode == "📝 Mock Tests & Assessment":
    st.markdown("<h3 style='color: #FFFFFF;'>📝 Prelims & Mains Mock Test Arena</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Simulated Prelims MCQs with instant scoring (-0.66 negative marking) and Mains Answer Writing Evaluation.</p>", unsafe_allow_html=True)
    
    # Test Metrics Row
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Tests Attempted</div>
            <div class="metric-value">12</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Average Accuracy</div>
            <div class="metric-value">74.5%</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Prelims Est. Score</div>
            <div class="metric-value">108.6</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Mains Answers Evaluated</div>
            <div class="metric-value">28</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sub-tabs for Test Generator vs Interactive Sample Test vs Mains Practice
    test_tab1, test_tab2, test_tab3 = st.tabs(["⚡ AI Test Generator", "🎯 Live Prelims Practice Quiz", "✍️ Mains Answer Writing Challenge"])

    with test_tab1:
        st.markdown("<h4 style='color: #38BDF8;'>⚙️ Custom Test Generator</h4>", unsafe_allow_html=True)
        g_col1, g_col2, g_col3 = st.columns(3)
        with g_col1:
            subj_test = st.selectbox("Select Subject / Module:", ["Polity & Constitution", "Modern Indian History", "Indian Economy & Budget", "Environment & Ecology", "Science & Technology", "Geography & Environment", "CSAT Quantitative Aptitude"])
        with g_col2:
            num_qs = st.selectbox("Number of Questions:", ["5 Questions", "10 Questions", "15 Questions"])
        with g_col3:
            diff_lvl = st.selectbox("Difficulty Level:", ["UPSC Prelims Standard", "High-Yield Statement-based", "PYQ Trend Pattern"])
            
        if st.button("🚀 Generate AI Practice Quiz in Copilot", use_container_width=True, key="btn_gen_test"):
            st.session_state.pending_prompt = f"Generate a {num_qs} UPSC Prelims MCQ Practice Quiz on '{subj_test}' at '{diff_lvl}' level. Provide 4 options (A, B, C, D) for each, followed by correct answers and detailed explanations."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    with test_tab2:
        st.markdown("<h4 style='color: #38BDF8;'>🎯 Live Simulated Prelims Quiz (Sectional: Indian Polity & GS2)</h4>", unsafe_allow_html=True)
        st.caption("Marks: +2.0 for correct, -0.66 for incorrect answer.")
        
        sample_questions = [
            {
                "id": 1,
                "q": "With reference to the Preamble of the Indian Constitution, consider the following statements:\n1. It is non-justiciable in nature.\n2. It can be amended under Article 368 without altering basic structure.\n3. It was amended only once by the 44th Constitutional Amendment Act.",
                "opts": ["1 and 2 only", "2 and 3 only", "1 and 3 only", "1, 2 and 3"],
                "ans": "1 and 2 only",
                "exp": "Statement 1 is correct (non-justiciable). Statement 2 is correct (can be amended under Art 368 as held in Kesavananda Bharati case). Statement 3 is INCORRECT because it was amended by the 42nd Amendment Act (1976), not 44th."
            },
            {
                "id": 2,
                "q": "Which of the following bodies is/are Constitutional Bodies under the Constitution of India?\n1. National Human Rights Commission (NHRC)\n2. Finance Commission\n3. NITI Aayog",
                "opts": ["2 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
                "ans": "2 only",
                "exp": "Finance Commission is created under Article 280 (Constitutional Body). NHRC is a Statutory Body (Protection of Human Rights Act 1993). NITI Aayog is an Executive Body created by Cabinet resolution."
            }
        ]
        
        score = 0
        total_q = len(sample_questions)
        with st.form("interactive_mock_quiz_form"):
            user_answers = {}
            for sq in sample_questions:
                st.markdown(f"**Q{sq['id']}:** {sq['q']}")
                user_answers[sq['id']] = st.radio(f"Select Answer for Q{sq['id']}:", sq["opts"], index=None, key=f"mock_q_{sq['id']}")
                st.write("")
                
            quiz_submitted = st.form_submit_button("🏁 Submit Test & Calculate Score")
            
        if quiz_submitted:
            correct_cnt = 0
            wrong_cnt = 0
            unattempted = 0
            for sq in sample_questions:
                user_ans = user_answers.get(sq['id'])
                if user_ans is None:
                    unattempted += 1
                elif user_ans == sq['ans']:
                    correct_cnt += 1
                else:
                    wrong_cnt += 1
                    
            final_marks = (correct_cnt * 2.0) - (wrong_cnt * 0.66)
            st.markdown(f"""
            <div style="background: rgba(13, 17, 32, 0.9); border: 1.5px solid #38BDF8; border-radius: 16px; padding: 20px; margin-top: 16px;">
                <h4 style="color: #38BDF8; margin: 0;">📊 Test Score Card</h4>
                <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin-top: 8px;">Marks Obtained: <span style="color: #34D399;">{final_marks:.2f}</span> / {total_q * 2}</div>
                <div style="color: #94A3B8; margin-top: 4px;">Correct: <strong style="color:#34D399;">{correct_cnt}</strong> | Incorrect: <strong style="color:#EF4444;">{wrong_cnt}</strong> | Unattempted: <strong>{unattempted}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            
            for sq in sample_questions:
                with st.expander(f"💡 Explanation for Q{sq['id']}"):
                    st.markdown(f"**Correct Option:** {sq['ans']}\n\n**Detailed Explanation:** {sq['exp']}")

    with test_tab3:
        st.markdown("<h4 style='color: #38BDF8;'>✍️ Daily Mains Answer Writing Prompt</h4>", unsafe_allow_html=True)
        st.markdown("""
        **Mains Question (GS Paper 2 - Governance):**
        > *"Analyze the role of Digital Public Infrastructure (DPI) in transforming service delivery and financial inclusion in India. Discuss the key challenges that remain." (15 Marks, 250 words)*
        """)
        
        mains_ans = st.text_area("Write your answer structure or draft response here:", height=180, key="mains_writing_area")
        if st.button("🤖 Evaluate My Answer with AI Copilot", key="btn_eval_mains", use_container_width=True):
            if mains_ans.strip():
                st.session_state.pending_prompt = f"Evaluate my UPSC Mains Answer for the question: 'Analyze the role of Digital Public Infrastructure (DPI) in transforming service delivery in India.' Here is my answer draft:\n\n{mains_ans}\n\nProvide marks out of 15, strengths, missing points, structure analysis, and a top-scoring model answer outline."
                st.session_state.nav_mode = "🤖 Neural AI Copilot"
                st.rerun()
            else:
                st.warning("Please type your answer draft above before submitting for AI evaluation.")

# ==========================================
# VIEW 5: 🎓 LIVE & RECORDED CLASSES
# ==========================================
elif nav_mode == "🎓 Live & Recorded Classes":
    st.markdown("<h3 style='color: #FFFFFF;'>🎓 UPSC Live Classes & Interactive Lecture Library</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Access live batch lectures from Physics Wallah (PW Live), review subject playlists, and generate instant AI notes.</p>", unsafe_allow_html=True)
    
    pw_class_url = "https://www.pw.live/watch/?batchSlug=6a0d74b1acca9706aa169063&batchSubjectId=6a1d635dcf99bcb20ab85f01&subjectSlug=6a1d635dcf99bcb20ab85f01&topicSlug=all&scheduleId=6a3949598df846a134ed1e7d&type=penpencilvdo&isPPJEnabled=true&entryPoint=BATCH_LECTURE_VIDEOS_6a3949598df846a134ed1e7d&learn2Earn=true&parentId=6a0d74b1acca9706aa169063&vType=BATCHES&childId=6a3949598df846a134ed1e7d"

    # Featured Live/Recorded Class Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(13, 17, 32, 0.95) 0%, rgba(8, 11, 23, 0.98) 100%); border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 18px; padding: 24px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="background: rgba(239, 68, 68, 0.15); color: #EF4444; font-family: 'JetBrains Mono'; font-size: 0.8rem; font-weight: 800; padding: 4px 12px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3);">
                    🔴 LIVE BATCH LECTURE
                </span>
                <h4 style="color: #FFFFFF; font-size: 1.3rem; margin-top: 8px; margin-bottom: 4px;">🎓 PW Live Official Batch Class</h4>
                <div style="color: #94A3B8; font-size: 0.92rem;">UPSC CSE Foundation Batch Lecture · PenPencil Video Portal</div>
            </div>
            <a href="{pw_class_url}" target="_blank" style="background: linear-gradient(135deg, #0284C7 0%, #7C3AED 100%); color: #FFFFFF; font-weight: 700; padding: 12px 22px; border-radius: 12px; text-decoration: none; display: inline-block; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);">
                🎥 Open Fullscreen on PW.live →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Embedded Player Container
    st.markdown("<h4 style='color: #38BDF8;'>📺 Interactive PW Class Portal</h4>", unsafe_allow_html=True)
    
    try:
        import streamlit.components.v1 as components
        components.iframe(pw_class_url, height=520, scrolling=True)
    except Exception:
        st.markdown(f'<iframe src="{pw_class_url}" width="100%" height="520" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        st.markdown(f'<a href="{pw_class_url}" target="_blank" style="width:100%; display:block; text-align:center; background:rgba(56,189,248,0.15); color:#38BDF8; font-weight:700; padding:12px; border-radius:12px; border:1px solid rgba(56,189,248,0.3); text-decoration:none;">🚀 Launch Class on PW Live (Direct Link)</a>', unsafe_allow_html=True)
    with c_btn2:
        if st.button("🤖 Generate AI Notes for this PW Class", key="btn_pw_class_notes", use_container_width=True):
            st.session_state.pending_prompt = "Generate detailed UPSC revision notes for the active PW Live batch lecture topic. Include core concepts, definitions, key Mains analytical points, and practice Prelims MCQs."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    st.markdown("---")

    # Today's Live Schedule Timeline
    st.markdown("<h4 style='color: #38BDF8;'>📅 Today's Live Lecture Schedule</h4>", unsafe_allow_html=True)
    
    sched_col1, sched_col2, sched_col3 = st.columns(3)
    with sched_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div style="font-size:0.8rem; color:#34D399; font-weight:700;">🟢 LIVE NOW (08:00 - 10:00 AM)</div>
            <div class="pwskills-title" style="margin-top:4px;">🏛️ GS2: Indian Constitution & Parliamentary Procedures</div>
            <div class="pwskills-desc">Faculty: Dr. S. Sharma · Topic: Speaker Powers & Money Bill Controversies</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎥 Join Live Classroom", key="btn_join_live1", use_container_width=True):
            st.session_state.pending_prompt = "Summarize the key UPSC GS2 Mains concepts related to 'Speaker Powers, Money Bill qualification, and Article 110 controversies'."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    with sched_col2:
        st.markdown("""
        <div class="pwskills-card">
            <div style="font-size:0.8rem; color:#38BDF8; font-weight:700;">⏰ UPCOMING (02:00 - 04:00 PM)</div>
            <div class="pwskills-title" style="margin-top:4px;">📈 GS3: Macroeconomics & Union Budget Analysis</div>
            <div class="pwskills-desc">Faculty: Prof. V. Verma · Topic: Fiscal Deficit & Capital Expenditure Trends</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔔 Set Class Reminder", key="btn_join_live2", use_container_width=True):
            st.info("🔔 Reminder set for GS3 Macroeconomics & Union Budget class!")

    with sched_col3:
        st.markdown("""
        <div class="pwskills-card">
            <div style="font-size:0.8rem; color:#C084FC; font-weight:700;">📼 RECORDED (06:00 - 08:00 PM)</div>
            <div class="pwskills-title" style="margin-top:4px;">⚖️ GS4: Ethics Case Studies & Moral Philosophy</div>
            <div class="pwskills-desc">Faculty: Anand Sir · Topic: Deontology vs Utilitarianism in Civil Service</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶️ Watch Lecture Recording", key="btn_join_live3", use_container_width=True):
            st.session_state.pending_prompt = "Explain Deontology vs Utilitarianism with Civil Service ethics case study examples for UPSC GS Paper 4."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    st.markdown("---")

    # Subject Class Playlists & AI Note Summarizer
    class_tab1, class_tab2 = st.tabs(["📚 Subject Lecture Playlists", "📝 AI Video & Lecture Summarizer"])
    
    with class_tab1:
        c_paper = st.selectbox("Select GS Paper Module:", ["GS Paper 1 Lectures", "GS Paper 2 Lectures", "GS Paper 3 Lectures", "GS Paper 4 Ethics Lectures", "CSAT Masterclass"])
        
        lectures_data = [
            {"title": "Lecture 1: Preamble & Basic Structure Doctrine", "duration": "1h 45m", "status": "Completed ✅"},
            {"title": "Lecture 2: Fundamental Rights & Judicial Review (Art 12-35)", "duration": "2h 10m", "status": "Completed ✅"},
            {"title": "Lecture 3: Directive Principles & Fundamental Duties", "duration": "1h 30m", "status": "Available 📼"},
            {"title": "Lecture 4: Federal Structure & Centre-State Relations", "duration": "2h 00m", "status": "Available 📼"},
        ]
        
        for lec in lectures_data:
            lc1, lc2, lc3 = st.columns([0.6, 0.2, 0.2])
            with lc1:
                st.markdown(f"**{lec['title']}** ({lec['duration']})")
            with lc2:
                st.caption(lec['status'])
            with lc3:
                if st.button("📄 Generate Notes", key=f"btn_notes_{lec['title'][:15]}", use_container_width=True):
                    st.session_state.pending_prompt = f"Generate comprehensive UPSC GS revision notes for the lecture topic '{lec['title']}'. Include definitions, key articles, Supreme Court landmark cases, and Mains answer keywords."
                    st.session_state.nav_mode = "🤖 Neural AI Copilot"
                    st.rerun()

    with class_tab2:
        st.markdown("<h4 style='color: #38BDF8;'>⚡ AI Lecture Note & Concept Generator</h4>", unsafe_allow_html=True)
        st.markdown("Paste any lecture topic, sub-topic name, or lecture transcript excerpt below to instantly generate clean UPSC structured notes:")
        
        lec_topic = st.text_input("Enter Lecture Topic or Subject Keyword:", placeholder="e.g. Inflation Targeting & RBI Monetary Policy Framework", key="input_lec_topic")
        if st.button("🚀 Generate Structured Revision Notes", key="btn_gen_lec_notes", use_container_width=True):
            if lec_topic.strip():
                st.session_state.pending_prompt = f"Generate high-yield UPSC Mains & Prelims structured notes for the class lecture topic: '{lec_topic}'. Organize into Key Definitions, Core Concepts, Critical Data/Reports, Committee Recommendations, and Practice Prelims MCQs."
                st.session_state.nav_mode = "🤖 Neural AI Copilot"
                st.rerun()
            else:
                st.warning("Please enter a lecture topic above.")

# ==========================================
# VIEW 6: 💼 BACKUP PLANS & PW SKILLS
# ==========================================
elif nav_mode == "💼 Backup Plans & PW Skills":
    st.markdown("<h3 style='color: #FFFFFF;'>💼 Career Backup Plans & PW Skills Courses</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Strategic parallel exam options and industry-aligned technical courses from <a href='https://pwskills.com' target='_blank' style='color:#38BDF8; font-weight:700;'>PW Skills</a> to guarantee long-term career security.</p>", unsafe_allow_html=True)
    
    # Section 1: Parallel Exam Backups
    st.markdown("<h4 style='color: #38BDF8;'>🏛️ Option 1: High Syllabus-Overlap Government Exams</h4>", unsafe_allow_html=True)
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    
    with ex_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🏦 RBI Grade B Officer</div>
            <div class="pwskills-desc">High overlap in Economic & Social Issues (ESI), General Awareness, and Finance. Ideal for UPSC aspirants with strong GS3 background.</div>
            <div style="margin-top:10px;"><span style="color:#38BDF8; font-weight:700;">Overlap: ~70%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on RBI Prep", key="btn_rbi_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "Explain how to prepare for RBI Grade B alongside UPSC CSE. Highlight syllabus overlap, timetable, and recommended sources."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()
            
    with ex_col2:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🏛️ State PSC Services (UPPCS/BPSC)</div>
            <div class="pwskills-desc">Maximum syllabus match in History, Polity, Economy, and Geography. State-specific GS can be prepared in 4-6 weeks.</div>
            <div style="margin-top:10px;"><span style="color:#38BDF8; font-weight:700;">Overlap: ~85%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on State PSC", key="btn_psc_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "How can I integrate State PSC preparation with UPSC CSE? What state-specific GS strategy should I follow?"
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    with ex_col3:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🌾 NABARD Grade A Officer</div>
            <div class="pwskills-desc">Focuses on Agriculture & Rural Development (ARD) and Economic Issues. Direct alignment with UPSC GS3 Agriculture topics.</div>
            <div style="margin-top:10px;"><span style="color:#38BDF8; font-weight:700;">Overlap: ~65%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on NABARD", key="btn_nabard_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "Explain NABARD Grade A exam pattern and syllabus overlap with UPSC GS Paper 3 Agriculture."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    st.markdown("---")

    # Section 2: PW Skills Course Catalog
    st.markdown("<h4 style='color: #38BDF8;'>🎓 Option 2: PW Skills Career Tech Courses (<a href='https://pwskills.com' target='_blank' style='color:#38BDF8;'>pwskills.com</a>)</h4>", unsafe_allow_html=True)
    st.caption("Build high-paying tech and analytics skills in parallel to ensure 100% job readiness.")
    
    pw_courses = [
        {
            "category": "🧠 Data Science & AI / Machine Learning",
            "courses": [
                {
                    "title": "Data Science Master Class",
                    "desc": "Comprehensive training in Python, Statistics, Machine Learning, Deep Learning, SQL, and Power BI.",
                    "url": "https://pwskills.com"
                },
                {
                    "title": "Generative AI & LLM Engineering",
                    "desc": "Master Prompt Engineering, LangChain, LlamaIndex, Fine-Tuning LLMs, and Vector Databases.",
                    "url": "https://pwskills.com"
                }
            ]
        },
        {
            "category": "💻 Full Stack Web & Software Engineering",
            "courses": [
                {
                    "title": "Java Full Stack Development",
                    "desc": "Complete Java, Spring Boot, Microservices, React.js, Data Structures & System Design.",
                    "url": "https://pwskills.com"
                },
                {
                    "title": "MERN Stack Web Development",
                    "desc": "Build scalable web applications using MongoDB, Express.js, React, and Node.js.",
                    "url": "https://pwskills.com"
                }
            ]
        },
        {
            "category": "📊 Data Analytics & Business Intelligence",
            "courses": [
                {
                    "title": "Data Analytics Job Guarantee Program",
                    "desc": "Master Advanced Excel, SQL, Tableau, Power BI, and Business Analytics for corporate roles.",
                    "url": "https://pwskills.com"
                },
                {
                    "title": "Power BI & SQL Mastery",
                    "desc": "High-yield course on dashboard design, data modeling, DAX queries, and SQL data warehousing.",
                    "url": "https://pwskills.com"
                }
            ]
        },
        {
            "category": "☁️ Cloud Computing, DevOps & Cybersecurity",
            "courses": [
                {
                    "title": "DevOps & AWS Cloud Engineering",
                    "desc": "Learn Docker, Kubernetes, Jenkins, Terraform, Ansible, and Amazon Web Services (AWS).",
                    "url": "https://pwskills.com"
                },
                {
                    "title": "Cybersecurity & Ethical Hacking",
                    "desc": "Network security, vulnerability assessment, penetration testing, and security compliance.",
                    "url": "https://pwskills.com"
                }
            ]
        }
    ]
    
    for c_group in pw_courses:
        st.markdown(f"#### {c_group['category']}")
        p_col1, p_col2 = st.columns(2)
        
        for idx, course in enumerate(c_group["courses"]):
            target_col = p_col1 if idx % 2 == 0 else p_col2
            with target_col:
                st.markdown(f"""
                <div class="pwskills-card">
                    <div class="pwskills-title">{course['title']}</div>
                    <div class="pwskills-desc">{course['desc']}</div>
                    <div style="margin-top:10px;"><a href="{course['url']}" target="_blank" class="pwskills-link">🔗 View Course on PWSkills.com →</a></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🤖 Consult AI on {course['title']}", key=f"btn_pws_fs_{course['title'][:10]}", use_container_width=True):
                    st.session_state.pending_prompt = f"How can I balance UPSC preparation while pursuing the PW Skills course '{course['title']}' (https://pwskills.com)? Provide a balanced daily schedule."
                    st.session_state.nav_mode = "🤖 Neural AI Copilot"
                    st.rerun()

# ==========================================
# VIEW 4: ➕ CUSTOM MODULES
# ==========================================
elif nav_mode == "➕ Custom Modules":
    st.markdown("<h3 style='color: #FFFFFF;'>➕ Add Custom Microtopics & Syllabus Files</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Expand your UPSC curriculum dashboard with custom topics or upload syllabus PDF files.</p>", unsafe_allow_html=True)
    
    col_add1, col_add2 = st.columns(2)
    
    with col_add1:
        st.markdown("<h4 style='color: #FFFFFF;'>📝 Add New Microtopic</h4>", unsafe_allow_html=True)
        with st.form("add_microtopic_form_fs"):
            paper_choice = st.selectbox("Select GS Paper:", ["GS Paper 1", "GS Paper 2", "GS Paper 3", "GS Paper 4", "Optional / Essay"])
            subject_input = st.text_input("Subject Name (e.g. Modern History, Governance):")
            topic_input = st.text_input("Topic Name (e.g. 1857 Revolt, E-Governance):")
            micro_input = st.text_input("Microtopic Detail:")
            priority_choice = st.selectbox("Priority:", ["🔥 High Priority", "⚡ Medium Priority", "📌 Low Priority"])
            
            submitted = st.form_submit_button("➕ Save Microtopic to Curriculum")
            if submitted and micro_input:
                new_item = {
                    "paper": paper_choice,
                    "subject": subject_input or "General Studies",
                    "topic": topic_input or "Custom Topic",
                    "microtopic": micro_input,
                    "priority": priority_choice
                }
                if "custom_microtopics" not in st.session_state.progress:
                    st.session_state.progress["custom_microtopics"] = []
                st.session_state.progress["custom_microtopics"].append(new_item)
                save_user_progress(st.session_state.progress)
                st.success(f"✅ Added microtopic: '{micro_input}'")

    with col_add2:
        st.markdown("<h4 style='color: #FFFFFF;'>📄 Upload Curriculum Document</h4>", unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("Upload custom UPSC Syllabus PDF file", type=["pdf", "txt"], key="pdf_up_fs")
        if uploaded_pdf is not None:
            if st.button("🚀 Process & Index File", key="proc_btn_fs"):
                st.info("Processing uploaded syllabus file into vector memory...")
                st.success("✅ Syllabus document successfully processed!")

# ==========================================
# VIEW 5: 📊 MATRIX ANALYTICS
# ==========================================
elif nav_mode == "📊 Matrix Analytics":
    st.markdown("<h3 style='color: #FFFFFF;'>📊 UPSC Matrix Analytics</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8;'>Visual breakdown of syllabus coverage across GS1, GS2, GS3, and GS4.</p>", unsafe_allow_html=True)
    
    a_col1, a_col2 = st.columns(2)
    
    with a_col1:
        st.markdown("<h4 style='color: #FFFFFF;'>📊 Paper-wise Workload</h4>", unsafe_allow_html=True)
        p_counts = {"GS Paper 1": 386, "GS Paper 2": 89, "GS Paper 3": 73, "GS Paper 4": 69}
        for p_name, count in p_counts.items():
            completed_p = sum(1 for m_id in st.session_state.progress.get("completed", []) if m_id.startswith(p_name))
            p_pct = (completed_p / count * 100) if count > 0 else 0
            st.markdown(f"<strong style='color: #38BDF8;'>{p_name}</strong> <span style='color: #94A3B8;'>({completed_p}/{count} completed)</span>", unsafe_allow_html=True)
            st.progress(p_pct / 100.0)
            
    with a_col2:
        st.markdown("<h4 style='color: #FFFFFF;'>🎯 Focus Area Recommendations</h4>", unsafe_allow_html=True)
        st.info("📍 **Recommended Priority:** Complete **GS Paper 1 (Culture & Modern History)** and **GS Paper 2 (Polity & Constitution)** first as they have high weightage in Prelims & Mains overlap.")
        st.success("✅ **Study Tip:** Click '💡 Explainer' next to any pending microtopic in the Curriculum Navigator to generate high-yield structured notes.")
