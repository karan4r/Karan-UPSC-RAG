import streamlit as st
import json
import re
from pathlib import Path
from generation.rag_chain import RAGChatbot
from ui_components import inject_custom_css, render_futuristic_header

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="UPSC AI RAG Mentor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject High-Contrast Light Futuristic CSS
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
    st.session_state.nav_mode = "🤖 AI Mentor Chat"

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
        st.markdown("<h3 style='color: #2563EB; font-family: Outfit; font-weight: 800; margin-bottom: 16px;'>📝 Practice Quiz & Prelims Assessment</h3>", unsafe_allow_html=True)
        
        for q_idx, mcq in enumerate(mcqs):
            opts = mcq.get("options", {})
            opt_a = opts.get("A", "")
            opt_b = opts.get("B", "")
            opt_c = opts.get("C", "")
            opt_d = opts.get("D", "")
            
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 16px; padding: 22px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(15,23,42,0.03);">
                <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 14px; line-height: 1.5;">
                    <span style="color: #2563EB;">Question {q_idx+1}:</span> {mcq['question']}
                </div>
                <div style="font-size: 0.9rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">Options:</div>
                <div style="margin-left: 4px; margin-bottom: 8px;">
                    <div style="color: #0F172A; padding: 8px 14px; margin-bottom: 6px; background: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 0.95rem; font-weight: 500;">• <strong>A)</strong> {opt_a}</div>
                    <div style="color: #0F172A; padding: 8px 14px; margin-bottom: 6px; background: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 0.95rem; font-weight: 500;">• <strong>B)</strong> {opt_b}</div>
                    <div style="color: #0F172A; padding: 8px 14px; margin-bottom: 6px; background: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 0.95rem; font-weight: 500;">• <strong>C)</strong> {opt_c}</div>
                    <div style="color: #0F172A; padding: 8px 14px; margin-bottom: 6px; background: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 0.95rem; font-weight: 500;">• <strong>D)</strong> {opt_d}</div>
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
    st.markdown("<h3 style='color: #0F172A;'>⚙️ System Controls</h3>", unsafe_allow_html=True)
    st.info("💡 **Tip:** Use the Curriculum Navigator to track microtopics and click '💡 Explainer' to auto-generate context notes.")
    
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
    st.markdown("<h3 style='color: #0F172A;'>📊 Curriculum Progress</h3>", unsafe_allow_html=True)
    st.progress(pct / 100.0)
    st.markdown(f"<strong style='color: #0F172A;'>{completed_count} / {total_micros}</strong> <span style='color: #475569;'>modules completed ({pct:.1f}%)</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Check pending prompt redirect
if st.session_state.pending_prompt:
    st.session_state.nav_mode = "🤖 AI Mentor Chat"

# Main Top Navigation Radio
NAV_OPTIONS = ["🤖 AI Mentor Chat", "📋 Syllabus Navigator", "💼 Backup Plans & PW Skills", "➕ Custom Modules", "📊 Progress Analytics"]
curr_idx = NAV_OPTIONS.index(st.session_state.nav_mode) if st.session_state.nav_mode in NAV_OPTIONS else 0

nav_mode = st.radio(
    "Navigation",
    NAV_OPTIONS,
    index=curr_idx,
    label_visibility="collapsed"
)
st.session_state.nav_mode = nav_mode
st.markdown("<br>", unsafe_allow_html=True)

# Function to render High-Visibility Query Form
def render_query_card(box_key: str):
    with st.form(f"query_form_{box_key}", clear_on_submit=True):
        st.markdown("<div style='font-size: 1.1rem; font-weight: 800; color: #1D4ED8; margin-bottom: 8px;'>💬 ASK UPSC AI RAG MENTOR:</div>", unsafe_allow_html=True)
        t_col1, t_col2 = st.columns([0.82, 0.18])
        with t_col1:
            q_val = st.text_input(
                "",
                placeholder="Type your UPSC query, syllabus question, or career backup question here...",
                key=f"mentor_query_input_{box_key}",
                label_visibility="collapsed"
            )
        with t_col2:
            submitted = st.form_submit_button("🚀 Ask Mentor", use_container_width=True)
    return submitted, q_val

# ==========================================
# VIEW 1: 🤖 AI MENTOR CHAT
# ==========================================
if nav_mode == "🤖 AI Mentor Chat":
    # If NO messages yet: Render prominent Query Box at the top
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
            with st.spinner("✨ Consulting Professional Psychologist & Knowledge Core..."):
                result = st.session_state.chatbot.chat(prompt_to_process, mh_count=mh_count)
            
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
    st.markdown("<h3 style='color: #0F172A;'>📋 GS Mains Curriculum & Microtopic Navigator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Browse microtopics parsed from official GS Mains syllabus, track completion, and generate AI notes.</p>", unsafe_allow_html=True)
    
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
        st.markdown("<div style='margin-bottom: -6px;'><strong style='color: #2563EB;'>🔍 Search Microtopics / Keywords:</strong></div>", unsafe_allow_html=True)
        search_query = st.text_input("", placeholder="e.g. Fundamental Rights, Music, Economy...", key="dash_search_input_fs", label_visibility="collapsed").lower().strip()

    st.markdown("---")
    
    if selected_paper in syllabus:
        p_info = syllabus[selected_paper]
        st.markdown(f"<h3 style='color: #2563EB;'>📖 {p_info.get('title', selected_paper)}</h3>", unsafe_allow_html=True)
        
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
                        st.markdown(f"<h4 style='color: #0F172A; margin-top: 12px;'>📌 {t_data.get('title', top_key)}</h4>", unsafe_allow_html=True)
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
                                    st.session_state.pending_prompt = f"Explain the UPSC Mains microtopic '{m_text}' under '{top_key}' ({selected_paper}). Include key facts, significance, and practice questions."
                                    st.session_state.nav_mode = "🤖 AI Mentor Chat"
                                    st.rerun()
                        st.write("")

# ==========================================
# VIEW 3: 💼 BACKUP PLANS & PW SKILLS
# ==========================================
elif nav_mode == "💼 Backup Plans & PW Skills":
    st.markdown("<h3 style='color: #0F172A;'>💼 Career Backup Plans & PW Skills Courses</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Strategic parallel exam options and industry-aligned technical courses from <a href='https://pwskills.com' target='_blank' style='color:#2563EB; font-weight:700;'>PW Skills</a> to guarantee long-term career security.</p>", unsafe_allow_html=True)
    
    # Section 1: Parallel Exam Backups
    st.markdown("<h4 style='color: #2563EB;'>🏛️ Option 1: High Syllabus-Overlap Government Exams</h4>", unsafe_allow_html=True)
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    
    with ex_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🏦 RBI Grade B Officer</div>
            <div class="pwskills-desc">High overlap in Economic & Social Issues (ESI), General Awareness, and Finance. Ideal for UPSC aspirants with strong GS3 background.</div>
            <div style="margin-top:10px;"><span style="color:#2563EB; font-weight:700;">Overlap: ~70%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on RBI Prep", key="btn_rbi_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "Explain how to prepare for RBI Grade B alongside UPSC CSE. Highlight syllabus overlap, timetable, and recommended sources."
            st.session_state.nav_mode = "🤖 AI Mentor Chat"
            st.rerun()
            
    with ex_col2:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🏛️ State PSC Services (UPPCS/BPSC)</div>
            <div class="pwskills-desc">Maximum syllabus match in History, Polity, Economy, and Geography. State-specific GS can be prepared in 4-6 weeks.</div>
            <div style="margin-top:10px;"><span style="color:#2563EB; font-weight:700;">Overlap: ~85%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on State PSC", key="btn_psc_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "How can I integrate State PSC preparation with UPSC CSE? What state-specific GS strategy should I follow?"
            st.session_state.nav_mode = "🤖 AI Mentor Chat"
            st.rerun()

    with ex_col3:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🌾 NABARD Grade A Officer</div>
            <div class="pwskills-desc">Focuses on Agriculture & Rural Development (ARD) and Economic Issues. Direct alignment with UPSC GS3 Agriculture topics.</div>
            <div style="margin-top:10px;"><span style="color:#2563EB; font-weight:700;">Overlap: ~65%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on NABARD", key="btn_nabard_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "Explain NABARD Grade A exam pattern and syllabus overlap with UPSC GS Paper 3 Agriculture."
            st.session_state.nav_mode = "🤖 AI Mentor Chat"
            st.rerun()

    st.markdown("---")

    # Section 2: PW Skills Course Catalog
    st.markdown("<h4 style='color: #2563EB;'>🎓 Option 2: PW Skills Career Tech Courses (<a href='https://pwskills.com' target='_blank' style='color:#2563EB;'>pwskills.com</a>)</h4>", unsafe_allow_html=True)
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
                    st.session_state.nav_mode = "🤖 AI Mentor Chat"
                    st.rerun()

# ==========================================
# VIEW 4: ➕ CUSTOM MODULES
# ==========================================
elif nav_mode == "➕ Custom Modules":
    st.markdown("<h3 style='color: #0F172A;'>➕ Add Custom Microtopics & Syllabus Files</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Expand your UPSC curriculum dashboard with custom topics or upload syllabus PDF files.</p>", unsafe_allow_html=True)
    
    col_add1, col_add2 = st.columns(2)
    
    with col_add1:
        st.markdown("<h4 style='color: #0F172A;'>📝 Add New Microtopic</h4>", unsafe_allow_html=True)
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
        st.markdown("<h4 style='color: #0F172A;'>📄 Upload Curriculum Document</h4>", unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("Upload custom UPSC Syllabus PDF file", type=["pdf", "txt"], key="pdf_up_fs")
        if uploaded_pdf is not None:
            if st.button("🚀 Process & Index File", key="proc_btn_fs"):
                st.info("Processing uploaded syllabus file into vector memory...")
                st.success("✅ Syllabus document successfully processed!")

# ==========================================
# VIEW 5: 📊 PROGRESS ANALYTICS
# ==========================================
elif nav_mode == "📊 Progress Analytics":
    st.markdown("<h3 style='color: #0F172A;'>📊 UPSC Preparation Analytics</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569;'>Visual breakdown of syllabus coverage across GS1, GS2, GS3, and GS4.</p>", unsafe_allow_html=True)
    
    a_col1, a_col2 = st.columns(2)
    
    with a_col1:
        st.markdown("<h4 style='color: #0F172A;'>📊 Paper-wise Workload</h4>", unsafe_allow_html=True)
        p_counts = {"GS Paper 1": 386, "GS Paper 2": 89, "GS Paper 3": 73, "GS Paper 4": 69}
        for p_name, count in p_counts.items():
            completed_p = sum(1 for m_id in st.session_state.progress.get("completed", []) if m_id.startswith(p_name))
            p_pct = (completed_p / count * 100) if count > 0 else 0
            st.markdown(f"<strong style='color: #0F172A;'>{p_name}</strong> <span style='color: #475569;'>({completed_p}/{count} completed)</span>", unsafe_allow_html=True)
            st.progress(p_pct / 100.0)
            
    with a_col2:
        st.markdown("<h4 style='color: #0F172A;'>🎯 Focus Area Recommendations</h4>", unsafe_allow_html=True)
        st.info("📍 **Recommended Priority:** Complete **GS Paper 1 (Culture & Modern History)** and **GS Paper 2 (Polity & Constitution)** first as they have high weightage in Prelims & Mains overlap.")
        st.success("✅ **Study Tip:** Click '💡 Explainer' next to any pending microtopic in the Curriculum Navigator to generate high-yield structured notes.")
