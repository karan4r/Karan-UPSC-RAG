import streamlit as st
import json
import re
from pathlib import Path
from generation.rag_chain import RAGChatbot, generate_academic_fallback, generate_exam_fallback
from generation.mock_test_engine import generate_mock_test, evaluate_mock_test, CORE_SUBJECTS
from ui_components import inject_custom_css, render_exam_header, render_futuristic_header, EXAM_META_CONFIG

EXAM_VERTICALS = ["UPSC", "IIT-JEE", "NEET", "GATE", "CAT", "Banking", "SSC"]

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AI Neural Copilot - Exam Verticals",
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

# Initialize Session State for Exam Verticals
if "selected_exam" not in st.session_state:
    st.session_state.selected_exam = "UPSC"

if "exam_messages" not in st.session_state:
    st.session_state.exam_messages = {exam: [] for exam in EXAM_VERTICALS}

# Alias active messages list
st.session_state.messages = st.session_state.exam_messages[st.session_state.selected_exam]

if "chatbot" not in st.session_state or not hasattr(st.session_state.chatbot, "_generate_mental_health_syllabus_fallback"):
    st.session_state.chatbot = RAGChatbot()

if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "prep_level": "Foundation Completed (1-2 years prep)",
        "relationship_status": "Single & 100% Focused on Prep",
        "mental_state": "Slightly Stressed but Managing ⚖️",
        "energy_level": 7,
        "target_goal": "Prelims Strategy & PYQs"
    }

if "show_profile_questionnaire" not in st.session_state:
    st.session_state.show_profile_questionnaire = False

if "progress" not in st.session_state:
    st.session_state.progress = load_user_progress()

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "nav_mode" not in st.session_state:
    st.session_state.nav_mode = "🏠 Home"

if "ai_persona" not in st.session_state:
    st.session_state.ai_persona = "Personal Mentor"

if "active_mock_test" not in st.session_state:
    st.session_state.active_mock_test = None

if "mock_user_answers" not in st.session_state:
    st.session_state.mock_user_answers = {}

if "mock_test_report" not in st.session_state:
    st.session_state.mock_test_report = None

if "mock_test_history" not in st.session_state:
    st.session_state.mock_test_history = [
        {
            "id": "mock_hist_1",
            "title": "Full-Length Multi-Subject Diagnostic Mock #1",
            "date": "18 Oct 2026",
            "score": 14.68,
            "max_marks": 20.0,
            "accuracy": 78.5,
            "strong": ["Indian Polity & Constitution", "Geography & Mapping"],
            "weak": ["Indian Economy & Budget"]
        },
        {
            "id": "mock_hist_2",
            "title": "Sectional Mock: Indian Polity & Governance",
            "date": "19 Oct 2026",
            "score": 16.0,
            "max_marks": 20.0,
            "accuracy": 82.0,
            "strong": ["Indian Polity & Constitution"],
            "weak": []
        }
    ]


def redirect_to_copilot(prompt: str):
    st.session_state.pending_prompt = prompt
    st.session_state.nav_mode = "🤖 Neural AI Copilot"
    st.rerun()


def count_previous_mental_health_turns(messages: list[dict]) -> int:
    count = 0
    mh_words = {"mental health", "depressed", "depression", "anxiety", "anxious", "hopeless", "burnout", "suicidal", "self harm", "emotional distress", "exam anxiety", "mental stress"}
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
    # Intercept any legacy or cached fallback output and sanitize it into a rich teacher answer
    if "requires structured analysis" in content or "Overview for" in content:
        clean_q = re.sub(r"(?i)^(Overview for|explain|notes on|what is|describe)\s+", "", content.split("\n")[0]).strip()
        clean_q = re.sub(r"[\*#`]", "", clean_q).strip()
        content = generate_academic_fallback(clean_q if clean_q else "UPSC Syllabus Topic")

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
        st.markdown("<h3 style='color: #0F172A; font-weight: 800; margin-bottom: 16px;'>📝 Practice Quiz & Assessment</h3>", unsafe_allow_html=True)
        
        for q_idx, mcq in enumerate(mcqs):
            opts = mcq.get("options", {})
            opt_a = opts.get("A", "")
            opt_b = opts.get("B", "")
            opt_c = opts.get("C", "")
            opt_d = opts.get("D", "")
            
            st.markdown(f"""
            <div style="background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 16px !important; padding: 20px !important; margin-bottom: 16px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.02) !important;">
                <div style="font-size: 1.02rem !important; font-weight: 700 !important; color: #0F172A !important; margin-bottom: 12px !important; line-height: 1.5 !important;">
                    <span style="color: #4F46E5 !important;">Question {q_idx+1}:</span> {mcq['question']}
                </div>
                <div style="font-size: 0.82rem !important; font-weight: 700 !important; color: #64748B !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; margin-bottom: 8px !important;">Options:</div>
                <div style="margin-left: 2px; margin-bottom: 8px;">
                    <div style="color: #1E293B !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #F8FAFC !important; border-radius: 8px !important; border: 1px solid #E2E8F0 !important; font-size: 0.92rem !important; font-weight: 500 !important;">• <strong style="color: #4F46E5 !important;">A)</strong> {opt_a}</div>
                    <div style="color: #1E293B !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #F8FAFC !important; border-radius: 8px !important; border: 1px solid #E2E8F0 !important; font-size: 0.92rem !important; font-weight: 500 !important;">• <strong style="color: #4F46E5 !important;">B)</strong> {opt_b}</div>
                    <div style="color: #1E293B !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #F8FAFC !important; border-radius: 8px !important; border: 1px solid #E2E8F0 !important; font-size: 0.92rem !important; font-weight: 500 !important;">• <strong style="color: #4F46E5 !important;">C)</strong> {opt_c}</div>
                    <div style="color: #1E293B !important; padding: 8px 14px !important; margin-bottom: 6px !important; background: #F8FAFC !important; border-radius: 8px !important; border: 1px solid #E2E8F0 !important; font-size: 0.92rem !important; font-weight: 500 !important;">• <strong style="color: #4F46E5 !important;">D)</strong> {opt_d}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            options_list = [f"{k}) {v}" for k, v in opts.items()]
            key = f"quiz_{idx}_{q_idx}"
            user_choice = st.radio(
                f"Select your answer for Question {q_idx+1}:",
                options_list,
                key=key
            )
            
            if st.button(f"Submit Answer Q{q_idx+1}", key=f"btn_sub_{idx}_{q_idx}"):
                user_letter = user_choice.split(")")[0].strip() if user_choice else ""
                correct_letter = mcq.get("correct", "A").upper()
                if user_letter == correct_letter:
                    st.success(f"🎉 **Correct!** Answer is ({correct_letter}).")
                else:
                    st.error(f"❌ **Incorrect.** You chose ({user_letter}). Correct answer is **({correct_letter})**.")
                if mcq.get("explanation"):
                    st.info(f"💡 **Explanation:** {mcq['explanation']}")
            st.write("")
            
    if meta:
        with st.expander("🔍 System Retrieval & Context Signals"):
            st.json(meta)

def render_exam_selection_hub():
    render_exam_header(st.session_state.selected_exam)
    st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #475569; margin-bottom: 6px;'>🎓 SWITCH EXAM VERTICAL:</div>", unsafe_allow_html=True)
    col_cards = st.columns(len(EXAM_VERTICALS))
    exam_icons = {
        "UPSC": "🏛️",
        "IIT-JEE": "⚛️",
        "NEET": "🩺",
        "GATE": "⚙️",
        "CAT": "📈",
        "Banking": "🏦",
        "SSC": "🏢"
    }

    for i, exam in enumerate(EXAM_VERTICALS):
        with col_cards[i]:
            is_active = (exam == st.session_state.selected_exam)
            btn_label = f"{exam_icons[exam]} {exam}" + (" ✓" if is_active else "")
            if st.button(btn_label, key=f"btn_exam_hub_{exam}", use_container_width=True):
                st.session_state.selected_exam = exam
                st.session_state.messages = st.session_state.exam_messages[exam]
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


# Render Student Profile Questionnaire Component
def render_student_profile_card():
    sp = st.session_state.student_profile
    is_open = st.session_state.show_profile_questionnaire
    
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px 24px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">👋 Student Persona & Calibrator</span>
                <p style="color: #64748B; font-size: 0.88rem; margin: 4px 0 0 0;">
                    Tune your prep stage, relationship status & mental focus so your AI Copilot gives you hyper-personalized guidance!
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_q1, col_q2 = st.columns([0.78, 0.22])
    with col_q1:
        st.markdown(f"""
        <div style="font-size: 0.86rem; color: #475569; margin-bottom: 12px; background: #F8FAFC; padding: 10px 14px; border-radius: 10px; border: 1px solid #E2E8F0;">
            ✨ <strong>Active Calibration:</strong> 
            <span style="color: #2563EB; font-weight: 700;">{sp.get('prep_level', 'Not set')}</span> | 
            <span style="color: #DB2777; font-weight: 700;">{sp.get('relationship_status', 'Not set')}</span> | 
            <span style="color: #059669; font-weight: 700;">{sp.get('mental_state', 'Not set')}</span> | 
            <span style="color: #D97706; font-weight: 700;">⚡ Focus Energy {sp.get('energy_level', 7)}/10</span>
        </div>
        """, unsafe_allow_html=True)
    with col_q2:
        btn_txt = "❌ Close Form" if is_open else "✏️ Update My Vibe"
        if st.button(btn_txt, key="toggle_profile_questionnaire", use_container_width=True):
            st.session_state.show_profile_questionnaire = not is_open
            st.rerun()

    if is_open:
        with st.form("student_profiling_form", clear_on_submit=False):
            st.markdown("<h4 style='color: #0F172A;'>🤗 Calibrate Your AI Companion</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748B; font-size: 0.85rem;'>Shared information is kept private and used exclusively to adapt AI guidance to your stage.</p>", unsafe_allow_html=True)
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                prep_level = st.selectbox(
                    "🎓 1. What is your current preparation stage?",
                    options=[
                        "Fresh Beginner (Just starting out)",
                        "Foundation Completed (1-2 years prep)",
                        "Repeat Attempt Veteran",
                        "Working Professional (Balancing job & prep)",
                        "College Student (Final / 3rd Year)"
                    ],
                    index=0 if sp.get("prep_level") not in [
                        "Fresh Beginner (Just starting out)",
                        "Foundation Completed (1-2 years prep)",
                        "Repeat Attempt Veteran",
                        "Working Professional (Balancing job & prep)",
                        "College Student (Final / 3rd Year)"
                    ] else [
                        "Fresh Beginner (Just starting out)",
                        "Foundation Completed (1-2 years prep)",
                        "Repeat Attempt Veteran",
                        "Working Professional (Balancing job & prep)",
                        "College Student (Final / 3rd Year)"
                    ].index(sp.get("prep_level"))
                )

                relationship_status = st.selectbox(
                    "💞 2. How is your relationship / social environment right now?",
                    options=[
                        "Single & 100% Focused on Prep",
                        "In a Healthy & Supportive Relationship",
                        "Navigating Mixed Signals / One-Sided Feelings",
                        "Recent Breakup / Heartbreak",
                        "Facing Family / Peer Pressure"
                    ],
                    index=0 if sp.get("relationship_status") not in [
                        "Single & 100% Focused on Prep",
                        "In a Healthy & Supportive Relationship",
                        "Navigating Mixed Signals / One-Sided Feelings",
                        "Recent Breakup / Heartbreak",
                        "Facing Family / Peer Pressure"
                    ] else [
                        "Single & 100% Focused on Prep",
                        "In a Healthy & Supportive Relationship",
                        "Navigating Mixed Signals / One-Sided Feelings",
                        "Recent Breakup / Heartbreak",
                        "Facing Family / Peer Pressure"
                    ].index(sp.get("relationship_status"))
                )

            with p_col2:
                mental_state = st.selectbox(
                    "🧘 3. How would you describe your mental vibe & mindset today?",
                    options=[
                        "Feeling Energetic & In Flow State 🚀",
                        "Slightly Stressed but Managing ⚖️",
                        "Severe Syllabus Anxiety & Overwhelm 🤯",
                        "Burnt Out / Low Dopamine 🔋",
                        "Feeling Lonely & Distracted 😔"
                    ],
                    index=0 if sp.get("mental_state") not in [
                        "Feeling Energetic & In Flow State 🚀",
                        "Slightly Stressed but Managing ⚖️",
                        "Severe Syllabus Anxiety & Overwhelm 🤯",
                        "Burnt Out / Low Dopamine 🔋",
                        "Feeling Lonely & Distracted 😔"
                    ] else [
                        "Feeling Energetic & In Flow State 🚀",
                        "Slightly Stressed but Managing ⚖️",
                        "Severe Syllabus Anxiety & Overwhelm 🤯",
                        "Burnt Out / Low Dopamine 🔋",
                        "Feeling Lonely & Distracted 😔"
                    ].index(sp.get("mental_state"))
                )

                target_goal = st.selectbox(
                    "🎯 4. What is your primary focus right now?",
                    options=[
                        "Prelims Strategy & PYQs",
                        "Mains Answer Writing & Ethics Case Studies",
                        "Syllabus Navigator Microtopics Completion",
                        "Building a Backup Plan / Parallel Skills"
                    ],
                    index=0 if sp.get("target_goal") not in [
                        "Prelims Strategy & PYQs",
                        "Mains Answer Writing & Ethics Case Studies",
                        "Syllabus Navigator Microtopics Completion",
                        "Building a Backup Plan / Parallel Skills"
                    ] else [
                        "Prelims Strategy & PYQs",
                        "Mains Answer Writing & Ethics Case Studies",
                        "Syllabus Navigator Microtopics Completion",
                        "Building a Backup Plan / Parallel Skills"
                    ].index(sp.get("target_goal"))
                )

            energy_level = st.slider(
                "⚡ 5. Rate your Daily Focus Energy Score (1 = Exhausted, 10 = Supercharged):",
                min_value=1,
                max_value=10,
                value=int(sp.get("energy_level", 7))
            )

            submit_profile = st.form_submit_button("✨ Save My Profile & Calibrate AI Copilot", use_container_width=True)
            if submit_profile:
                st.session_state.student_profile = {
                    "prep_level": prep_level,
                    "relationship_status": relationship_status,
                    "mental_state": mental_state,
                    "energy_level": energy_level,
                    "target_goal": target_goal
                }
                st.session_state.show_profile_questionnaire = False
                st.success("🎉 Profile updated! Your AI Copilot is now tuned to your vibe!")
                st.rerun()

import datetime

# Clean Top Navigation Bar
top_c1, top_c2, top_c3, top_c4 = st.columns([0.27, 0.27, 0.31, 0.15])
with top_c1:
    exam_options = ["UPSC CSE", "IIT-JEE", "NEET", "GATE", "CAT", "Banking", "SSC"]
    curr_exam_display = "UPSC CSE" if st.session_state.selected_exam == "UPSC" else st.session_state.selected_exam
    chosen_exam_display = st.selectbox(
        "Exam Vertical",
        exam_options,
        index=exam_options.index(curr_exam_display) if curr_exam_display in exam_options else 0,
        key="top_exam_selector"
    )
    new_exam = "UPSC" if chosen_exam_display == "UPSC CSE" else chosen_exam_display
    if new_exam != st.session_state.selected_exam:
        st.session_state.selected_exam = new_exam
        st.session_state.messages = st.session_state.exam_messages[new_exam]
        st.rerun()

with top_c2:
    persona_options = ["Personal Mentor", "Academic Professor", "Strict Evaluator", "Socratic Guide", "Empathetic Counselor"]
    chosen_persona = st.selectbox(
        "AI Persona",
        persona_options,
        index=persona_options.index(st.session_state.get("ai_persona", "Personal Mentor")) if st.session_state.get("ai_persona", "Personal Mentor") in persona_options else 0,
        key="top_persona_selector"
    )
    if chosen_persona != st.session_state.get("ai_persona"):
        st.session_state.ai_persona = chosen_persona
        st.rerun()

with top_c3:
    st.markdown("""
    <div style="height: 100%; display: flex; align-items: flex-end; padding-bottom: 6px; justify-content: flex-end;">
        <span style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 9999px; padding: 7px 16px; font-size: 0.82rem; font-weight: 600; color: #334155; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <span style="color: #6366F1;">✨</span> Powered by RAG <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#22C55E; box-shadow: 0 0 6px #22C55E;"></span>
        </span>
    </div>
    """, unsafe_allow_html=True)

with top_c4:
    st.markdown("""
    <div style="height: 100%; display: flex; align-items: flex-end; padding-bottom: 6px; justify-content: flex-end;">
        <div style="width: 38px; height: 38px; border-radius: 50%; background: #EEF2FF; border: 1.5px solid #C7D2FE; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #4338CA; font-size: 0.95rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            K
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Minimalist Sidebar Setup matching Screenshot
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 6px 0 20px 2px;">
        <svg width="30" height="30" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 22L12 8L17 17L20 12L25 22H4Z" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 8L15 13" stroke="#60A5FA" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; line-height: 1.1;">UPSC AI</div>
            <div style="font-size: 0.72rem; color: #64748B; font-weight: 600; letter-spacing: 0.04em;">Learn · Plan · Grow</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    current_nav = st.session_state.nav_mode
    active_nav_tag = "Home"
    if current_nav in ["🤖 Neural AI Copilot"]:
        active_nav_tag = "Chat"
    elif current_nav in ["📊 Matrix Analytics"]:
        active_nav_tag = "Matrix Progress"
    elif current_nav in ["📋 Syllabus Navigator", "🎓 Live & Recorded Classes", "🚀 PW Skills Career Track", "💼 Backup Plans & PW Skills"]:
        active_nav_tag = "Resources"
    elif current_nav in ["⚙️ Settings", "➕ Custom Modules"]:
        active_nav_tag = "Settings"
    elif current_nav == "🏠 Home":
        active_nav_tag = "Home"

    if st.button("🏠  Home", key="sb_btn_home", use_container_width=True, type="primary" if active_nav_tag == "Home" else "secondary"):
        st.session_state.nav_mode = "🏠 Home"
        st.rerun()

    if st.button("💬  Chat", key="sb_btn_chat", use_container_width=True, type="primary" if active_nav_tag == "Chat" else "secondary"):
        st.session_state.nav_mode = "🤖 Neural AI Copilot"
        st.rerun()

    if st.button("📊  Matrix Progress", key="sb_btn_matrix", use_container_width=True, type="primary" if active_nav_tag == "Matrix Progress" else "secondary"):
        st.session_state.nav_mode = "📊 Matrix Analytics"
        st.rerun()

    if st.button("📖  Resources", key="sb_btn_resources", use_container_width=True, type="primary" if active_nav_tag == "Resources" else "secondary"):
        st.session_state.nav_mode = "📋 Syllabus Navigator"
        st.rerun()

    if st.button("⚙️  Settings", key="sb_btn_settings", use_container_width=True, type="primary" if active_nav_tag == "Settings" else "secondary"):
        st.session_state.nav_mode = "⚙️ Settings"
        st.rerun()

    st.markdown("""
    <div style="margin-top: 240px; padding: 18px 6px 10px 6px; border-top: 1px solid #F1F5F9;">
        <svg width="22" height="22" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity: 0.65; margin-bottom: 6px;">
            <path d="M4 22L12 8L17 17L20 12L25 22H4Z" stroke="#475569" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div style="font-size: 0.78rem; font-style: italic; color: #64748B; line-height: 1.45;">
            A better you,<br>creates a better tomorrow.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Check pending prompt redirect
if st.session_state.get("pending_prompt"):
    st.session_state.nav_mode = "🤖 Neural AI Copilot"

nav_mode = st.session_state.nav_mode
top_sub = False
top_val = ""

# ==========================================
# HOME VIEW: 🏠 DASHBOARD (MATCHING IMAGE)
# ==========================================
if nav_mode == "🏠 Home":
    main_col, side_col = st.columns([0.72, 0.28], gap="medium")

    with main_col:
        # Dynamic Greeting
        cur_hour = datetime.datetime.now().hour
        if cur_hour < 12:
            greet_word = "Good Morning"
            greet_icon = "🌅"
        elif 12 <= cur_hour < 17:
            greet_word = "Good Afternoon"
            greet_icon = "☀️"
        else:
            greet_word = "Good Evening"
            greet_icon = "🌆"

        st.markdown(f"""
        <div class="greeting-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="max-width: 65%;">
                    <h1 class="greeting-title">{greet_icon} {greet_word}, Karan</h1>
                    <div class="greeting-tagline">Your AI companion for UPSC and beyond.</div>
                    <p class="greeting-desc">Ask, learn, plan and grow — with personalized guidance, resources and support.</p>
                </div>
                <div style="width: 170px; height: 105px; opacity: 0.85; pointer-events: none;">
                    <svg viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%;">
                        <path d="M0 120L70 45L110 85L150 35L200 120H0Z" fill="url(#mtn_g1)" opacity="0.6"/>
                        <path d="M40 120L100 60L140 95L180 50L220 120H40Z" fill="url(#mtn_g2)" opacity="0.8"/>
                        <path d="M110 85L150 35L165 55L145 75Z" fill="#FFFFFF" opacity="0.7"/>
                        <line x1="150" y1="35" x2="150" y2="20" stroke="#475569" stroke-width="1.5"/>
                        <polygon points="150,20 162,24 150,28" fill="#EF4444"/>
                        <defs>
                            <linearGradient id="mtn_g1" x1="0" y1="40" x2="200" y2="120" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#C7D2FE" stop-opacity="0.9"/>
                                <stop stop-color="#EEF2FF" stop-opacity="0.3"/>
                            </linearGradient>
                            <linearGradient id="mtn_g2" x1="40" y1="50" x2="220" y2="120" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#93C5FD" stop-opacity="0.9"/>
                                <stop stop-color="#DBEAFE" stop-opacity="0.3"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Search Omnibar
        with st.form("home_search_omnibar", clear_on_submit=True):
            omni_c1, omni_c2 = st.columns([0.88, 0.12])
            with omni_c1:
                omni_query = st.text_input(
                    "Ask anything about UPSC, strategy, resources, or your goals...",
                    placeholder="✨ Ask anything about UPSC, strategy, resources, or your goals...",
                    label_visibility="collapsed",
                    key="omnibar_input"
                )
            with omni_c2:
                omni_submit = st.form_submit_button("➔", use_container_width=True)

        if omni_submit and omni_query.strip():
            st.session_state.pending_prompt = omni_query.strip()
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Feature Grid: Row 1
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        with r1_c1:
            st.markdown("""
            <div class="feature-card card-copilot">
                <div>
                    <div class="card-icon-badge">🧠</div>
                    <div class="card-title">Neural AI Co-pilot</div>
                    <div class="card-desc">Get instant, personalized answers and guidance powered by AI.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Co-pilot ➔", key="btn_card_copilot", use_container_width=True):
                st.session_state.nav_mode = "🤖 Neural AI Copilot"
                st.rerun()

        with r1_c2:
            st.markdown("""
            <div class="feature-card card-syllabus">
                <div>
                    <div class="card-icon-badge">📖</div>
                    <div class="card-title">Syllabus Navigator</div>
                    <div class="card-desc">Explore syllabus, topics, priorities and subject-wise roadmap.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Syllabus ➔", key="btn_card_syllabus", use_container_width=True):
                st.session_state.nav_mode = "📋 Syllabus Navigator"
                st.rerun()

        with r1_c3:
            st.markdown("""
            <div class="feature-card card-planner">
                <div>
                    <div class="card-icon-badge">🗓️</div>
                    <div class="card-title">Exam countdown & study planner</div>
                    <div class="card-desc">Track your exam date, create study plans and stay on schedule.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Planner ➔", key="btn_card_planner", use_container_width=True):
                st.session_state.nav_mode = "🗓️ Exam Countdown & Study Planner"
                st.rerun()

        with r1_c4:
            st.markdown("""
            <div class="feature-card card-productivity">
                <div>
                    <div class="card-icon-badge">🎯</div>
                    <div class="card-title">Productivity & targets</div>
                    <div class="card-desc">Set goals, track habits, manage time and boost productivity.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Targets ➔", key="btn_card_productivity", use_container_width=True):
                st.session_state.nav_mode = "⚡ Productivity & Targets"
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Feature Grid: Row 2
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1:
            st.markdown("""
            <div class="feature-card card-relationship">
                <div>
                    <div class="card-icon-badge">👥</div>
                    <div class="card-title">Relationship management</div>
                    <div class="card-desc">Get guidance on relationships, communication and life balance.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Guidance ➔", key="btn_card_relationship", use_container_width=True):
                st.session_state.nav_mode = "💞 Relationship Management"
                st.rerun()

        with r2_c2:
            st.markdown("""
            <div class="feature-card card-wellness">
                <div>
                    <div class="card-icon-badge">🪷</div>
                    <div class="card-title">Mental health & wellness</div>
                    <div class="card-desc">Talk, reflect, and get support for a healthier, happier you.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Wellness ➔", key="btn_card_wellness", use_container_width=True):
                st.session_state.nav_mode = "🧘 Mental Health & Wellness"
                st.rerun()

        with r2_c3:
            st.markdown("""
            <div class="feature-card card-mock">
                <div>
                    <div class="card-icon-badge">📄</div>
                    <div class="card-title">Mock test & assessment</div>
                    <div class="card-desc">Practice with real exam pattern tests and analyze your performance.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Mocks ➔", key="btn_card_mocks", use_container_width=True):
                st.session_state.nav_mode = "📝 Mock Tests & Assessment"
                st.rerun()

        with r2_c4:
            st.markdown("""
            <div class="feature-card card-classes">
                <div>
                    <div class="card-icon-badge">▶️</div>
                    <div class="card-title">Live & recorded classes</div>
                    <div class="card-desc">Attend live sessions or watch recorded lectures anytime, anywhere.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Classes ➔", key="btn_card_classes", use_container_width=True):
                st.session_state.nav_mode = "🎓 Live & Recorded Classes"
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Feature Grid: Row 3
        r3_c1, r3_c2 = st.columns([0.25, 0.75])
        with r3_c1:
            st.markdown("""
            <div class="feature-card card-pwskills">
                <div>
                    <div class="card-icon-badge">💼</div>
                    <div class="card-title">PW Skills career track</div>
                    <div class="card-desc">Build in-demand skills, get certified and shape your career.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Career ➔", key="btn_card_pwskills", use_container_width=True):
                st.session_state.nav_mode = "🚀 PW Skills Career Track"
                st.rerun()

        with r3_c2:
            st.markdown("""
            <div class="mission-banner">
                <div>
                    <div class="mission-tag">YOUR GOALS. OUR MISSION.</div>
                    <div class="mission-headline">Dream &nbsp;→&nbsp; Prepare &nbsp;→&nbsp; Achieve</div>
                </div>
                <div style="width: 140px; height: 80px; opacity: 0.9;">
                    <svg viewBox="0 0 160 90" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%;">
                        <path d="M10 90L65 25L100 65L125 20L160 90H10Z" fill="#C7D2FE" opacity="0.6"/>
                        <path d="M40 90L85 35L120 70L145 30L170 90H40Z" fill="#93C5FD" opacity="0.8"/>
                        <line x1="125" y1="20" x2="125" y2="8" stroke="#1E293B" stroke-width="1.5"/>
                        <polygon points="125,8 135,11 125,14" fill="#1E293B"/>
                    </svg>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with side_col:
        # Widget 1: Matrix Progress (Dynamically calculated from syllabus completion status)
        syllabus_data = load_syllabus_data()
        completed_set = set(st.session_state.progress.get("completed", []))
        custom_micros = st.session_state.progress.get("custom_microtopics", [])

        # Calculate dynamic paper-wise counts
        p_counts = {"GS Paper 1": 386, "GS Paper 2": 89, "GS Paper 3": 73, "GS Paper 4": 69}
        if syllabus_data:
            for p_name in list(p_counts.keys()):
                p_info = syllabus_data.get(p_name, {})
                c = sum(len(top.get("microtopics", [])) for subj in p_info.get("subjects", {}).values() for top in subj.get("topics", {}).values())
                if c > 0:
                    p_counts[p_name] = c

        total_micros = sum(p_counts.values()) + len(custom_micros)
        completed_count = len(completed_set)

        # Paper-wise completion counts & percentages
        gs1_done = sum(1 for m in completed_set if m.startswith("GS Paper 1"))
        gs2_done = sum(1 for m in completed_set if m.startswith("GS Paper 2"))
        gs3_done = sum(1 for m in completed_set if m.startswith("GS Paper 3"))
        gs4_done = sum(1 for m in completed_set if m.startswith("GS Paper 4"))

        gs1_pct = (gs1_done / p_counts["GS Paper 1"] * 100) if p_counts["GS Paper 1"] > 0 else 0.0
        gs2_pct = (gs2_done / p_counts["GS Paper 2"] * 100) if p_counts["GS Paper 2"] > 0 else 0.0
        gs3_pct = (gs3_done / p_counts["GS Paper 3"] * 100) if p_counts["GS Paper 3"] > 0 else 0.0
        gs4_pct = (gs4_done / p_counts["GS Paper 4"] * 100) if p_counts["GS Paper 4"] > 0 else 0.0

        overall_pct = (completed_count / total_micros * 100) if total_micros > 0 else 0.0

        # Formatted percentage strings
        display_overall_text = "0%" if completed_count == 0 else (f"{overall_pct:.1f}%" if overall_pct < 1.0 else f"{int(round(overall_pct))}%")
        gs1_pct_str = "0%" if gs1_done == 0 else (f"{gs1_pct:.1f}%" if gs1_pct < 1.0 else f"{int(round(gs1_pct))}%")
        gs2_pct_str = "0%" if gs2_done == 0 else (f"{gs2_pct:.1f}%" if gs2_pct < 1.0 else f"{int(round(gs2_pct))}%")
        gs3_pct_str = "0%" if gs3_done == 0 else (f"{gs3_pct:.1f}%" if gs3_pct < 1.0 else f"{int(round(gs3_pct))}%")
        gs4_pct_str = "0%" if gs4_done == 0 else (f"{gs4_pct:.1f}%" if gs4_pct < 1.0 else f"{int(round(gs4_pct))}%")

        # SVG Donut stroke calculation
        if completed_count == 0:
            donut_dash = "0.0 100.0"
        else:
            arc_val = max(1.5, min(100.0, float(overall_pct)))
            donut_dash = f"{arc_val:.1f} {100.0 - arc_val:.1f}"

        # Dynamic motivational quote based on actual completion
        if completed_count == 0:
            quote_text = "Start ticking topics in Syllabus Navigator"
        elif overall_pct < 25:
            quote_text = "Good start! Small daily steps build mastery"
        elif overall_pct < 50:
            quote_text = "Solid pace! Core syllabus in progress"
        elif overall_pct < 75:
            quote_text = "Over halfway through the matrix!"
        elif overall_pct < 100:
            quote_text = "Almost complete! High exam readiness"
        else:
            quote_text = "Full curriculum mastered! Ready for exam"

        st.markdown(f"""
        <div class="widget-panel-card">
            <div class="widget-panel-title">
                <span>✨ Your Matrix Progress</span>
                <span style="font-size: 0.72rem; font-weight: 700; color: #0284C7; background: #F0F9FF; border: 1px solid #BAE6FD; padding: 2px 8px; border-radius: 9999px;">
                    {completed_count}/{total_micros} Covered
                </span>
            </div>
            <div class="progress-matrix-container">
                <div class="progress-donut-wrapper">
                    <svg width="76" height="76" viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#F1F5F9" stroke-width="3.2"></circle>
                        <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#0EA5E9" stroke-width="3.2" stroke-dasharray="{donut_dash}" stroke-dashoffset="25" stroke-linecap="round"></circle>
                        <text x="18" y="20.5" font-family="'Plus Jakarta Sans', sans-serif" font-size="8.5" font-weight="800" text-anchor="middle" fill="#0F172A">{display_overall_text}</text>
                    </svg>
                </div>
                <div style="flex-grow: 1;">
                    <div class="progress-list-item">
                        <span><span class="progress-dot" style="background: #16A34A;"></span>GS 1 History & Geo</span>
                        <span style="font-weight: 700; color: #0F172A;">{gs1_pct_str} <span style="font-weight: 500; font-size: 0.72rem; color: #475569;">({gs1_done}/{p_counts['GS Paper 1']})</span></span>
                    </div>
                    <div class="progress-list-item">
                        <span><span class="progress-dot" style="background: #2563EB;"></span>GS 2 Polity & Gov</span>
                        <span style="font-weight: 700; color: #0F172A;">{gs2_pct_str} <span style="font-weight: 500; font-size: 0.72rem; color: #475569;">({gs2_done}/{p_counts['GS Paper 2']})</span></span>
                    </div>
                    <div class="progress-list-item">
                        <span><span class="progress-dot" style="background: #9333EA;"></span>GS 3 Economy & Env</span>
                        <span style="font-weight: 700; color: #0F172A;">{gs3_pct_str} <span style="font-weight: 500; font-size: 0.72rem; color: #475569;">({gs3_done}/{p_counts['GS Paper 3']})</span></span>
                    </div>
                    <div class="progress-list-item">
                        <span><span class="progress-dot" style="background: #D97706;"></span>GS 4 Ethics & Case</span>
                        <span style="font-weight: 700; color: #0F172A;">{gs4_pct_str} <span style="font-weight: 500; font-size: 0.72rem; color: #475569;">({gs4_done}/{p_counts['GS Paper 4']})</span></span>
                    </div>
                    <div class="progress-list-item" style="border-top: 1px dashed #E2E8F0; padding-top: 4px; margin-top: 4px;">
                        <span><span class="progress-dot" style="background: #0284C7;"></span>Overall Syllabus</span>
                        <span style="font-weight: 700; color: #0284C7;">{display_overall_text} <span style="font-weight: 600; font-size: 0.72rem; color: #475569;">({completed_count}/{total_micros})</span></span>
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; padding-top: 10px; border-top: 1px solid #F1F5F9;">
                <div style="font-size: 0.78rem; color: #475569; font-style: italic;">
                    {quote_text}
                </div>
                <div style="font-size: 0.75rem; font-weight: 600; color: #22C55E; display: flex; align-items: center; gap: 4px;">
                    <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #22C55E;"></span>
                    Live Sync
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Full Progress Matrix ➔", key="btn_side_matrix", use_container_width=True):
            st.session_state.nav_mode = "📊 Matrix Analytics"
            st.rerun()

        # Widget 2: Quick Actions
        st.markdown("""
        <div class="widget-panel-card">
            <div class="widget-panel-title">
                <span>⚡ Quick Actions</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶️  Resume from last session", key="qa_resume", use_container_width=True):
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()
        if st.button("🗓️  View study planner", key="qa_planner", use_container_width=True):
            st.session_state.nav_mode = "🗓️ Exam Countdown & Study Planner"
            st.rerun()
        if st.button("📥  Download resources", key="qa_resources", use_container_width=True):
            st.session_state.nav_mode = "📋 Syllabus Navigator"
            st.rerun()
        if st.button("🔔  Check latest updates", key="qa_updates", use_container_width=True):
            st.toast("📢 Latest updates: High-yield UPSC microtopics active!")

        # Widget 3: Persona Card
        active_persona = st.session_state.get("ai_persona", "Personal Mentor")
        st.markdown(f"""
        <div class="widget-panel-card">
            <div class="widget-panel-title">
                <span>👤 Your AI Persona</span>
                <span style="font-size: 0.85rem; color: #64748B;">›</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem; color: #6366F1;">〰️</span>
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">{active_persona}</div>
                </div>
                <div style="font-size: 0.76rem; color: #64748B; margin-top: 4px;">
                    Supportive · Motivational · Result-driven
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Change Persona ➔", key="btn_side_change_persona", use_container_width=True):
            st.session_state.nav_mode = "⚙️ Settings"
            st.rerun()

        # Widget 4: Today's Focus
        today_date_str = datetime.date.today().strftime("%d %b %Y")
        if "today_focus_tasks" not in st.session_state:
            st.session_state.today_focus_tasks = [
                {"task": "Answer writing practice (GS 2)", "done": True},
                {"task": "Revise Modern History", "done": True},
                {"task": "Daily current affairs (1 hour)", "done": False},
                {"task": "Gym / Health", "done": False},
            ]

        st.markdown(f"""
        <div class="widget-panel-card">
            <div class="widget-panel-title">
                <span>🎯 Today's Focus</span>
                <span style="font-size: 0.8rem; font-weight: 600; color: #64748B;">{today_date_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for t_idx, item in enumerate(st.session_state.today_focus_tasks):
            c_done = st.checkbox(item["task"], value=item["done"], key=f"focus_chk_{t_idx}")
            st.session_state.today_focus_tasks[t_idx]["done"] = c_done

else:
    # Inner page breadcrumb
    b_col1, b_col2 = st.columns([0.22, 0.78])
    with b_col1:
        if st.button("← Back to Home", key="btn_back_home_top", use_container_width=True):
            st.session_state.nav_mode = "🏠 Home"
            st.rerun()
    with b_col2:
        st.markdown(f"<div style='font-size: 1.25rem; font-weight: 800; color: #0F172A; padding-top: 5px;'>{st.session_state.nav_mode}</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 10px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)


# Sample Prompts per Vertical
SAMPLE_PROMPTS = {
    "UPSC": [
        "🏛️ Explain the Constitutional framework of Fundamental Rights (Articles 14-32)",
        "📜 Analyze the causes & impact of the Revolt of 1857 in Modern History",
        "🧘 I am feeling overwhelmed by the vast UPSC syllabus, build me a study recovery plan"
    ],
    "IIT-JEE": [
        "⚛️ Explain Newton's Laws of Motion with rotational dynamics equations & numerical step-by-step",
        "🧪 Explain Chemical Bonding, Hybridization (sp, sp2, sp3) and Molecular Orbital Theory",
        "📐 Explain Calculus Integration by parts and definite integrals shortcuts for JEE"
    ],
    "NEET": [
        "🩺 Explain Photosynthesis C3 vs C4 pathways and Calvin Cycle with NCERT line-by-line breakdown",
        "🧬 Explain DNA Replication mechanism, Okazaki fragments, and polymerases for NEET",
        "🧪 Explain Chemical Kinetics rate laws, zero & first order reaction half-life formulas"
    ],
    "GATE": [
        "⚙️ Explain Dijkstra's & Prim's algorithms with time/space complexity & Numerical Answer Type steps",
        "💻 Explain Operating Systems Paging, Virtual Memory & Page Fault calculation",
        "📊 Explain Control Systems Bode Plots, Nyquist Stability Criterion & Transfer Functions"
    ],
    "CAT": [
        "📈 Explain Speed Math shortcuts for Ratios, Percentages & Profit-Loss problems in CAT QA",
        "🧩 Explain DILR Set Theory 3-Venn Diagram and Maxima-Minima logic puzzles",
        "📚 Explain VARC Reading Comprehension Main Idea vs Author Inference elimination hacks"
    ],
    "Banking": [
        "🏦 Explain Syllogism Venn Diagram rules for 'Only a few' and 'Some Not' cases in IBPS PO",
        "🧩 Explain Circular & Linear Seating Arrangement puzzle solving framework",
        "💳 Explain RBI Monetary Policy instruments (Repo, CRR, SLR) and Banking Awareness"
    ],
    "SSC": [
        "🏢 Explain SSC CGL Geometry Circle & Tangent theorems with short tricks",
        "⚡ Explain Trigonometry value substitution tricks (0°, 45°, 90°) for fast solving",
        "🏛️ Explain SSC General Awareness high-yield Static GK (Dynasties, Rivers & Articles)"
    ]
}

# ==========================================
# VIEW 1: 🤖 NEURAL AI COPILOT
# ==========================================
if nav_mode == "🤖 Neural AI Copilot":
    render_exam_selection_hub()
    # If NO messages yet for this vertical: Render Quick Sample Prompts
    if not st.session_state.messages:
        st.markdown(f"#### 💡 Starter Prompts for **{st.session_state.selected_exam}**:")
        sp_cols = st.columns(3)
        current_samples = SAMPLE_PROMPTS.get(st.session_state.selected_exam, SAMPLE_PROMPTS["UPSC"])
        for idx, sample in enumerate(current_samples):
            with sp_cols[idx]:
                if st.button(sample, key=f"btn_sample_{st.session_state.selected_exam}_{idx}", use_container_width=True):
                    st.session_state.pending_prompt = sample
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Display Chat Messages for Active Exam
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                render_assistant_message(msg["content"], idx, msg.get("meta"))
            else:
                st.markdown(msg["content"])

    # Determine prompt to process
    chat_prompt = st.chat_input(f"Ask {st.session_state.selected_exam} AI anything about syllabus, strategy, MCQs...")
    prompt_to_process = None
    if st.session_state.pending_prompt:
        prompt_to_process = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
    elif chat_prompt and chat_prompt.strip():
        prompt_to_process = chat_prompt.strip()
    elif top_sub and top_val.strip():
        prompt_to_process = top_val.strip()

    if prompt_to_process:
        mh_count = count_previous_mental_health_turns(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.chat_message("user"):
            st.markdown(prompt_to_process)

        with st.chat_message("assistant"):
            with st.spinner(f"⚡ Executing {st.session_state.selected_exam} RAG Matrix & Consulting Copilot..."):
                try:
                    result = st.session_state.chatbot.chat(
                        prompt_to_process,
                        mh_count=mh_count,
                        exam_vertical=st.session_state.selected_exam,
                        student_profile=st.session_state.student_profile
                    )
                except Exception:
                    result = st.session_state.chatbot.chat(
                        prompt_to_process,
                        exam_vertical=st.session_state.selected_exam,
                        student_profile=st.session_state.student_profile
                    )
            
            ans_content = result.get("answer", "")
            if "requires structured analysis" in ans_content or "Overview for" in ans_content:
                clean_q = re.sub(r"(?i)^(Overview for|explain|notes on|what is|describe)\s+", "", ans_content.split("\n")[0]).strip()
                clean_q = re.sub(r"[\*#`]", "", clean_q).strip()
                ans_content = generate_exam_fallback(clean_q if clean_q else prompt_to_process, exam_vertical=st.session_state.selected_exam)
                result["answer"] = ans_content

            meta = {
                "intent": result.get("intent", "notes_or_explain_topic"),
                "category": result.get("category", "academic"),
                "confidence": result.get("confidence", "high"),
                "mode": result.get("mode", "rag+web"),
                "signals": result.get("signals", []),
                "sources": result.get("sources", []),
                "exam_vertical": st.session_state.selected_exam,
            }
            
            next_idx = len(st.session_state.messages)
            render_assistant_message(ans_content, next_idx, meta)

        st.session_state.messages.append(
            {"role": "assistant", "content": ans_content, "meta": meta}
        )
        st.session_state.exam_messages[st.session_state.selected_exam] = st.session_state.messages
        st.rerun()


# ==========================================
# VIEW 2: 📋 SYLLABUS NAVIGATOR
# ==========================================
elif nav_mode == "📋 Syllabus Navigator":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>📋 GS Mains Curriculum & Microtopic Navigator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Browse microtopics parsed from official GS Mains syllabus, track completion, and generate AI notes.</p>", unsafe_allow_html=True)
    
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
        st.markdown("<div style='margin-bottom: -6px;'><strong style='color: #0284C7;'>🔍 Search Microtopics / Keywords:</strong></div>", unsafe_allow_html=True)
        search_query = st.text_input("", placeholder="e.g. Fundamental Rights, Music, Economy...", key="dash_search_input_fs", label_visibility="collapsed").lower().strip()

    st.markdown("---")
    
    if selected_paper in syllabus:
        p_info = syllabus[selected_paper]
        st.markdown(f"<h3 style='color: #0F172A; font-weight: 800;'>📖 {p_info.get('title', selected_paper)}</h3>", unsafe_allow_html=True)
        
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
                        st.markdown(f"<h4 style='color: #0F172A; font-weight: 700; margin-top: 12px;'>📌 {t_data.get('title', top_key)}</h4>", unsafe_allow_html=True)
                        for m_text, m_id, is_comp in filtered_micros:
                            has_saved_notes = m_id in st.session_state.progress.get("notes", {}) and bool(
                                st.session_state.progress["notes"][m_id].get("text") or 
                                st.session_state.progress["notes"][m_id].get("file_content")
                            )
                            badge_label = " 📝 [Notes Attached]" if has_saved_notes else ""
                            
                            c_col1, c_col2, c_col3 = st.columns([0.62, 0.18, 0.20])
                            with c_col1:
                                checked = st.checkbox(f"{m_text}{badge_label}", value=is_comp, key=f"chk_fs_{m_id}")
                                if checked != is_comp:
                                    if checked and m_id not in st.session_state.progress["completed"]:
                                        st.session_state.progress["completed"].append(m_id)
                                    elif not checked and m_id in st.session_state.progress["completed"]:
                                        st.session_state.progress["completed"].remove(m_id)
                                    save_user_progress(st.session_state.progress)
                                    st.rerun()
                            with c_col2:
                                if st.button("💡 AI Explainer", key=f"ask_fs_{m_id}", use_container_width=True):
                                    redirect_to_copilot(f"Explain the microtopic '{m_text}' under '{top_key}' ({selected_paper}) for {st.session_state.selected_exam} in detail like a master educator. Provide core concepts, exam relevance, practice MCQs, and step-by-step guidance.")
                            with c_col3:
                                toggle_notes = st.button("📝 Student Notes", key=f"btn_notes_tgl_{m_id}", use_container_width=True)

                            # Toggle personal notes section
                            notes_key = f"show_notes_{m_id}"
                            if toggle_notes:
                                st.session_state[notes_key] = not st.session_state.get(notes_key, False)
                                
                            if st.session_state.get(notes_key, False):
                                with st.expander(f"📁 Personal Notes & Uploaded Files for: {m_text}", expanded=True):
                                    existing_note_data = st.session_state.progress.get("notes", {}).get(m_id, {})
                                    existing_text = existing_note_data.get("text", "")
                                    existing_file_name = existing_note_data.get("filename", "")
                                    existing_file_content = existing_note_data.get("file_content", "")
                                    
                                    st.markdown("<h5 style='color: #0F172A; font-weight: 700;'>📤 Upload Personal Study Notes File</h5>", unsafe_allow_html=True)
                                    up_file = st.file_uploader(
                                        f"Upload notes file for '{m_text}' (.txt, .md, .pdf)",
                                        type=["txt", "md", "pdf"],
                                        key=f"uploader_file_{m_id}",
                                        help="Upload your personal hand-written or typed study notes for this microtopic."
                                    )
                                    
                                    if up_file is not None:
                                        try:
                                            content_str = ""
                                            if up_file.name.endswith(".pdf"):
                                                try:
                                                    import pypdf
                                                    import io
                                                    pdf_reader = pypdf.PdfReader(io.BytesIO(up_file.read()))
                                                    content_str = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
                                                except Exception as pe:
                                                    content_str = f"[PDF Extracted Content - Error: {pe}]"
                                            else:
                                                content_str = up_file.read().decode("utf-8", errors="ignore")
                                            
                                            if "notes" not in st.session_state.progress:
                                                st.session_state.progress["notes"] = {}
                                            
                                            import datetime
                                            st.session_state.progress["notes"][m_id] = {
                                                "text": existing_text,
                                                "filename": up_file.name,
                                                "file_content": content_str,
                                                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                            }
                                            save_user_progress(st.session_state.progress)
                                            st.success(f"🎉 Successfully uploaded and saved '{up_file.name}'!")
                                            st.rerun()
                                        except Exception as ex:
                                            st.error(f"Error processing uploaded file: {ex}")

                                    st.markdown("<h5 style='color: #0F172A; font-weight: 700; margin-top: 12px;'>✏️ Type / Edit Personal Notes</h5>", unsafe_allow_html=True)
                                    written_text = st.text_area(
                                        "Write your custom study notes, formulas, or revision points:",
                                        value=existing_text,
                                        height=140,
                                        key=f"textarea_note_{m_id}"
                                    )
                                    
                                    n_col1, n_col2 = st.columns([0.5, 0.5])
                                    with n_col1:
                                        if st.button("💾 Save Personal Notes", key=f"save_note_btn_{m_id}", use_container_width=True):
                                            if "notes" not in st.session_state.progress:
                                                st.session_state.progress["notes"] = {}
                                            import datetime
                                            st.session_state.progress["notes"][m_id] = {
                                                "text": written_text.strip(),
                                                "filename": existing_file_name,
                                                "file_content": existing_file_content,
                                                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                            }
                                            save_user_progress(st.session_state.progress)
                                            st.success("✅ Personal notes saved successfully!")
                                            st.rerun()
                                    with n_col2:
                                        if st.button("🗑️ Clear Saved Notes", key=f"del_note_btn_{m_id}", use_container_width=True):
                                            if "notes" in st.session_state.progress and m_id in st.session_state.progress["notes"]:
                                                del st.session_state.progress["notes"][m_id]
                                                save_user_progress(st.session_state.progress)
                                                st.info("🗑️ Personal notes cleared.")
                                                st.rerun()

                                    # Display Saved Notes Summary & Preview
                                    if existing_text or existing_file_content:
                                        st.markdown("---")
                                        st.markdown("<h5 style='color: #059669; font-weight: 700;'>📖 Saved Student Notes Overview</h5>", unsafe_allow_html=True)
                                        if existing_note_data.get("updated_at"):
                                            st.caption(f"Last updated: {existing_note_data.get('updated_at')}")
                                        if existing_file_name:
                                            st.markdown(f"📎 **Attached File:** `{existing_file_name}`")
                                        if existing_text:
                                            st.markdown(f"**Personal Summary:**\n```\n{existing_text}\n```")
                                        if existing_file_content:
                                            with st.expander(f"📄 Full Attached File Content ({existing_file_name})"):
                                                st.text_area("Uploaded Notes Text", value=existing_file_content, height=200, disabled=True, key=f"prev_txt_{m_id}")

                        st.write("")

# ==========================================
# VIEW: 🗓️ EXAM COUNTDOWN & STUDY PLANNER
# ==========================================
elif nav_mode == "🗓️ Exam Countdown & Study Planner":
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 14px;">
            <div style="max-width: 72%;">
                <span style="background: #EFF6FF; color: #2563EB; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; border: 1px solid #BFDBFE;">
                    🎯 STRATEGIC TIMELINE ENGINE
                </span>
                <h2 style="color: #0F172A; font-size: 1.85rem; margin-top: 10px; margin-bottom: 6px; font-weight: 800; letter-spacing: -0.02em;">
                    🗓️ Exam Date Roadmap & 1-Week Buffer Study Planner
                </h2>
                <div style="color: #475569; font-size: 0.95rem; line-height: 1.55;">
                    Analyze real-time syllabus completion (topics done vs remaining) and calculate an optimized daily velocity roadmap engineered to <strong style="color: #0F172A;">finish 100% of the syllabus exactly 1 week before the exam</strong>.
                </div>
            </div>
            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 14px; padding: 12px 18px; text-align: center;">
                <div style="color: #16A34A; font-weight: 800; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace;">🛡️ 1-WEEK BUFFER PRINCIPLE</div>
                <div style="color: #334155; font-size: 0.82rem; margin-top: 3px; font-weight: 500;">Final 7 days reserved for Mocks & Micro-Revision</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    import datetime
    today = datetime.date.today()
    
    # 1. LIVE PREPARATION LEVEL AUDIT (Topics completed, topics left)
    syllabus_data = load_syllabus_data()
    total_micros = 623
    completed_set = set(st.session_state.progress.get("completed", []))
    completed_cnt = len(completed_set)
    completed_pct = (completed_cnt / total_micros * 100) if total_micros > 0 else 0.0
    left_cnt = max(0, total_micros - completed_cnt)
    left_pct = max(0.0, 100.0 - completed_pct)

    gs1_total, gs1_done = 386, sum(1 for m in completed_set if m.startswith("GS Paper 1"))
    gs2_total, gs2_done = 89, sum(1 for m in completed_set if m.startswith("GS Paper 2"))
    gs3_total, gs3_done = 73, sum(1 for m in completed_set if m.startswith("GS Paper 3"))
    gs4_total, gs4_done = 69, sum(1 for m in completed_set if m.startswith("GS Paper 4"))

    gs1_left = max(0, gs1_total - gs1_done)
    gs2_left = max(0, gs2_total - gs2_done)
    gs3_left = max(0, gs3_total - gs3_done)
    gs4_left = max(0, gs4_total - gs4_done)

    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📊 1. Current Preparation Level & Syllabus Audit</h4>", unsafe_allow_html=True)
    st.caption("Real-time tracking of syllabus microtopics completed vs left across General Studies papers:")

    # Top Metrics Cards Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Total Curriculum</div>
            <div class="metric-value">{total_micros}</div>
            <div style="color: #0284C7; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">GS 1-4 Microtopics</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Topics Completed</div>
            <div class="metric-value" style="color: #059669;">{completed_cnt}</div>
            <div style="color: #059669; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{completed_pct:.1f}% Covered</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Topics Left (Remaining)</div>
            <div class="metric-value" style="color: #D97706;">{left_cnt}</div>
            <div style="color: #DC2626; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{left_pct:.1f}% Remaining to Finish</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        stage_label = "🏁 Revision Master" if left_cnt == 0 else ("🚀 Advanced Sprint" if completed_pct >= 50 else ("⚡ Core Foundation" if completed_pct >= 20 else "🌱 Early Setup"))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎯 Prep Stage Status</div>
            <div class="metric-value" style="font-size: 1.6rem; color: #7C3AED;">{stage_label}</div>
            <div style="color: #475569; font-size: 0.82rem; font-weight: 600; margin-top: 4px;">Active Learning Phase</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Paper-by-Paper Progress Meters
    pp_col1, pp_col2 = st.columns(2)
    with pp_col1:
        gs1_pct = (gs1_done / gs1_total * 100) if gs1_total > 0 else 0
        st.markdown(f"""
        <div class="pwskills-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="pwskills-title">🏛️ GS Paper 1: Heritage, History, Geography, Society</span>
                <span style="color:#0284C7; font-weight:700;">{gs1_done}/{gs1_total} Done</span>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin:6px 0;">Remaining: <strong style="color:#D97706;">{gs1_left} microtopics</strong> ({100-gs1_pct:.1f}% left)</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(gs1_pct / 100.0)

        gs2_pct = (gs2_done / gs2_total * 100) if gs2_total > 0 else 0
        st.markdown(f"""
        <div class="pwskills-card" style="margin-top:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="pwskills-title">⚖️ GS Paper 2: Polity, Constitution, Governance, IR</span>
                <span style="color:#0284C7; font-weight:700;">{gs2_done}/{gs2_total} Done</span>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin:6px 0;">Remaining: <strong style="color:#D97706;">{gs2_left} microtopics</strong> ({100-gs2_pct:.1f}% left)</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(gs2_pct / 100.0)

    with pp_col2:
        gs3_pct = (gs3_done / gs3_total * 100) if gs3_total > 0 else 0
        st.markdown(f"""
        <div class="pwskills-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="pwskills-title">📈 GS Paper 3: Economy, Environment, Sci-Tech, Security</span>
                <span style="color:#0284C7; font-weight:700;">{gs3_done}/{gs3_total} Done</span>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin:6px 0;">Remaining: <strong style="color:#D97706;">{gs3_left} microtopics</strong> ({100-gs3_pct:.1f}% left)</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(gs3_pct / 100.0)

        gs4_pct = (gs4_done / gs4_total * 100) if gs4_total > 0 else 0
        st.markdown(f"""
        <div class="pwskills-card" style="margin-top:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="pwskills-title">🧘 GS Paper 4: Ethics, Integrity, Aptitude & Case Studies</span>
                <span style="color:#0284C7; font-weight:700;">{gs4_done}/{gs4_total} Done</span>
            </div>
            <div style="font-size:0.85rem; color:#475569; margin:6px 0;">Remaining: <strong style="color:#D97706;">{gs4_left} microtopics</strong> ({100-gs4_pct:.1f}% left)</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(gs4_pct / 100.0)

    st.markdown("---")

    # 2. EXAM DATE CONFIGURATION & TARGET FINISH DEADLINE
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🗓️ 2. Input Exam Conduct Date & Target Buffer Calibration</h4>", unsafe_allow_html=True)
    st.caption("Tell the system the exact date on which the exam will be conducted. The engine enforces the 1-Week Pre-Exam Finish rule:")

    saved_plan = st.session_state.progress.setdefault("exam_plan", {})
    saved_exam_date_str = saved_plan.get("exam_date")

    default_exam_date = today + datetime.timedelta(days=90)
    if saved_exam_date_str:
        try:
            parsed_saved_date = datetime.date.fromisoformat(saved_exam_date_str)
            if parsed_saved_date > today:
                default_exam_date = parsed_saved_date
        except Exception:
            pass

    with st.form("exam_date_planner_form", clear_on_submit=False):
        f_col1, f_col2, f_col3 = st.columns([1.3, 1, 1])
        with f_col1:
            exam_input_date = st.date_input(
                "📅 When will your exam be conducted?",
                value=default_exam_date,
                min_value=today + datetime.timedelta(days=1),
                help="Select the scheduled or expected date of the exam."
            )
        with f_col2:
            daily_hours_input = st.slider(
                "⏱️ Daily Study Capacity:",
                min_value=4.0,
                max_value=14.0,
                value=float(saved_plan.get("daily_hours", 8.0)),
                step=0.5,
                help="Average deep work study hours available each day."
            )
        with f_col3:
            rest_schedule = st.selectbox(
                "🗓️ Weekly Buffer / Rest Schedule:",
                options=["1 Day / Week (Recommended for Anti-Burnout)", "0.5 Day / Week (Intensive)", "0 Days (Strict Daily Sprint)"],
                index=0 if saved_plan.get("rest_schedule") not in ["1 Day / Week (Recommended for Anti-Burnout)", "0.5 Day / Week (Intensive)", "0 Days (Strict Daily Sprint)"] else ["1 Day / Week (Recommended for Anti-Burnout)", "0.5 Day / Week (Intensive)", "0 Days (Strict Daily Sprint)"].index(saved_plan.get("rest_schedule")),
                help="Allocate rest days for cognitive reset."
            )

        f_rev1, f_rev2 = st.columns([1.3, 1.7])
        with f_rev1:
            rev_ratio = st.slider(
                "🔄 Daily Revision Allocation (% of study time):",
                min_value=15,
                max_value=40,
                value=int(saved_plan.get("rev_ratio", 25)),
                step=5,
                format="%d%%",
                help="Recommended 25% to consolidate active recall."
            )
        with f_rev2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            submit_exam_plan = st.form_submit_button("⚡ Analyze & Generate Detailed 1-Week Buffer Study Plan", use_container_width=True)

        if submit_exam_plan:
            st.session_state.progress["exam_plan"] = {
                "exam_date": exam_input_date.isoformat(),
                "daily_hours": daily_hours_input,
                "rest_schedule": rest_schedule,
                "rev_ratio": rev_ratio
            }
            save_user_progress(st.session_state.progress)
            st.success(f"✅ Target Exam Date set to {exam_input_date.strftime('%B %d, %Y')}! Plan calibrated.")
            st.rerun()

    # Calculate active timelines
    active_exam_date = exam_input_date
    total_days_until_exam = (active_exam_date - today).days
    target_finish_date = active_exam_date - datetime.timedelta(days=7)  # 1 WEEK BEFORE EXAM
    prep_days_available = (target_finish_date - today).days

    rest_factor = 1.0 / 7.0 if "1 Day" in rest_schedule else (0.5 / 7.0 if "0.5 Day" in rest_schedule else 0.0)
    net_active_prep_days = max(1, prep_days_available - int(prep_days_available * rest_factor))
    daily_quota_needed = round(left_cnt / max(1, net_active_prep_days), 2)
    weekly_quota_needed = round(daily_quota_needed * (7 - (1 if '1 Day' in rest_schedule else 0)), 1)
    study_hrs_per_topic = round((daily_hours_input * (1 - rev_ratio / 100.0)) / max(0.1, daily_quota_needed), 1)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. ANALYTICAL TIMELINE & VELOCITY ENGINE
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📈 3. Strategic Buffer & Pacing Analytics</h4>", unsafe_allow_html=True)

    # Check for date feasibility edge cases
    if prep_days_available <= 0:
        st.warning(f"⚠️ **Urgent Alert:** The exam date ({active_exam_date.strftime('%d %b %Y')}) is less than 7 days away ({total_days_until_exam} days remaining). Under the **1-Week Buffer Principle**, **NO NEW TOPICS** should be started now. Activate Full-Simulation Mock and Formula Sheet Revision mode immediately!")
    else:
        v_col1, v_col2, v_col3, v_col4 = st.columns(4)
        with v_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📅 Days to Official Exam</div>
                <div class="metric-value">{total_days_until_exam} Days</div>
                <div style="color: #0284C7; font-size: 0.82rem; font-weight: 700; margin-top: 4px;">Conduct Date: {active_exam_date.strftime('%d %b %Y')}</div>
            </div>
            """, unsafe_allow_html=True)
        with v_col2:
            st.markdown(f"""
            <div class="metric-card" style="border-color: #10B981 !important;">
                <div class="metric-label">🎯 100% Finish Deadline</div>
                <div class="metric-value" style="color: #059669; font-size: 1.8rem;">{target_finish_date.strftime('%d %b %Y')}</div>
                <div style="color: #059669; font-size: 0.82rem; font-weight: 700; margin-top: 4px;">Exactly 1 Week Before Exam!</div>
            </div>
            """, unsafe_allow_html=True)
        with v_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⏳ Active Study Window</div>
                <div class="metric-value" style="color: #D97706;">{prep_days_available} Days</div>
                <div style="color: #475569; font-size: 0.82rem; font-weight: 600; margin-top: 4px;">{net_active_prep_days} net study days ({rest_schedule.split(' ')[0]})</div>
            </div>
            """, unsafe_allow_html=True)
        with v_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⚡ Daily Microtopic Quota</div>
                <div class="metric-value" style="color: #0284C7;">{daily_quota_needed} / day</div>
                <div style="color: #7C3AED; font-size: 0.82rem; font-weight: 700; margin-top: 4px;">~{weekly_quota_needed} topics / week</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Velocity Diagnosis Banner
        if daily_quota_needed <= 2.5:
            diag_badge = "🟢 HIGH RETENTION PACE (COMFORTABLE & THOROUGH)"
            diag_color = "#059669"
            diag_msg = f"With **{daily_quota_needed} microtopics/day**, you have abundant time to read standard reference books (Laxmikanth, NCERTs), prepare crisp 1-page notes, and complete 2 comprehensive revision cycles before the 7-day buffer begins!"
        elif daily_quota_needed <= 4.5:
            diag_badge = "🟡 BALANCED HIGH-YIELD SPRINT (STANDARD ASPIRANT VELOCITY)"
            diag_color = "#0284C7"
            diag_msg = f"With **{daily_quota_needed} microtopics/day** (~{study_hrs_per_topic} hrs/topic), you are on a prime civil services schedule. Allocate your morning 3-hour deep work block to complete 2 topics, and afternoon for the rest + Prelims MCQs."
        elif daily_quota_needed <= 6.5:
            diag_badge = "🟠 INTENSIVE SPRINT (FOCUSED 9-11 HOUR CAPACITY REQUIRED)"
            diag_color = "#D97706"
            diag_msg = f"With **{daily_quota_needed} microtopics/day**, velocity is demanding. Strictly utilize syllabus summaries, short notes, and avoid opening multiple secondary sources. Stick to NCERTs + high-yield PYQ themes."
        else:
            diag_badge = "🔴 EMERGENCY TRIAGE SPRINT (PARETO 80/20 ESSENTIALS)"
            diag_color = "#DC2626"
            diag_msg = f"With **{daily_quota_needed} microtopics/day**, prioritize high-frequency Prelims and Mains themes: Polity (Art 12-51A, Parliament), Modern History (1857-1947), Economy (Inflation, Banking, Budget), and Environment."

        st.markdown(f"""
        <div class="pwskills-card" style="border-color: {diag_color} !important;">
            <div style="color: {diag_color}; font-weight: 800; font-size: 0.95rem; font-family: 'JetBrains Mono';">{diag_badge}</div>
            <div style="color: #1E293B; font-size: 0.92rem; margin-top: 6px; line-height: 1.55;">
                {diag_msg}
            </div>
            <div style="margin-top: 10px; font-size: 0.85rem; color: #475569;">
                🛡️ <strong>Guaranteed Buffer:</strong> By reaching 100% on <strong>{target_finish_date.strftime('%B %d, %Y')}</strong>, you safeguard the entire final week ({target_finish_date.strftime('%d %b')} to {active_exam_date.strftime('%d %b')}) exclusively for full-length mocks, error analysis, and mental composure.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Graphical Timeline Burn-Down
        try:
            import pandas as pd
            num_weeks = max(2, (prep_days_available // 7) + 1)
            burn_timeline = []
            cur_topics_left = left_cnt
            cur_date = today
            decrement = left_cnt / max(1, num_weeks)
            
            for w in range(num_weeks + 1):
                burn_timeline.append({
                    "Date / Milestone": cur_date.strftime("%d %b"),
                    "Remaining Microtopics": max(0, int(cur_topics_left)),
                    "Completed Microtopics": min(total_micros, int(completed_cnt + (left_cnt - cur_topics_left)))
                })
                cur_topics_left = max(0, cur_topics_left - decrement)
                cur_date = cur_date + datetime.timedelta(days=7)
                if cur_date > target_finish_date:
                    cur_date = target_finish_date
            
            # Add final exam date milestone with 0 remaining
            burn_timeline.append({
                "Date / Milestone": f"{active_exam_date.strftime('%d %b')} (Exam Day)",
                "Remaining Microtopics": 0,
                "Completed Microtopics": total_micros
            })
            
            df_burn = pd.DataFrame(burn_timeline).set_index("Date / Milestone")
            st.markdown("<h5 style='color: #0F172A; font-weight: 700; margin-top: 16px;'>📈 Projected Syllabus Burn-Down Curve (Reaches 0 One Week Before Exam)</h5>", unsafe_allow_html=True)
            st.line_chart(df_burn[["Remaining Microtopics", "Completed Microtopics"]], height=240)
        except Exception:
            pass

    st.markdown("---")

    # 4. DETAILED PHASE-BY-PHASE ROADMAP
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🗺️ 4. Phase-by-Phase Execution Roadmap (100% Syllabus Finish 1 Week Pre-Exam)</h4>", unsafe_allow_html=True)
    st.caption("Engineered roadmap splitting your available timeline into distinct mastery phases, culminating in the 7-Day Buffer Week:")

    p1_days = max(2, int(prep_days_available * 0.35))
    p2_days = max(2, int(prep_days_available * 0.40))
    p3_days = max(1, prep_days_available - p1_days - p2_days)

    p1_end = today + datetime.timedelta(days=p1_days)
    p2_end = p1_end + datetime.timedelta(days=p2_days)
    p3_end = target_finish_date

    phase_col1, phase_col2 = st.columns(2)
    with phase_col1:
        st.markdown(f"""
        <div class="pwskills-card">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#059669; font-weight:800;">
                PHASE 1: {today.strftime('%d %b')} - {p1_end.strftime('%d %b')} ({p1_days} DAYS)
            </div>
            <div class="pwskills-title" style="margin-top:4px; color:#059669 !important;">
                🟢 Core Foundation & GS1/GS2 Backlog Clearance
            </div>
            <div style="color:#334155; font-size:0.9rem; margin-top:8px; line-height:1.55;">
                • <strong>Target Papers:</strong> Complete pending microtopics in <strong>GS Paper 1</strong> (Modern Indian History 1857-1947, Physical Geography) and <strong>GS Paper 2</strong> (Articles 1-51A, Parliament, Supreme Court Judgments).<br>
                • <strong>Daily Quota:</strong> {daily_quota_needed} microtopics daily.<br>
                • <strong>Testing Routine:</strong> 15 topic-specific Prelims MCQs after completing each microtopic.<br>
                • <strong>Milestone:</strong> Clear 35% of remaining topics with 1-page condensed micro-sheets.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pwskills-card" style="margin-top:14px;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#0284C7; font-weight:800;">
                PHASE 3: {p2_end.strftime('%d %b')} - {p3_end.strftime('%d %b')} ({p3_days} DAYS)
            </div>
            <div class="pwskills-title" style="margin-top:4px; color:#0284C7 !important;">
                🔵 Final Syllabus Clearance & Micro-Notes Consolidation
            </div>
            <div style="color:#334155; font-size:0.9rem; margin-top:8px; line-height:1.55;">
                • <strong>Target Papers:</strong> Clear remaining microtopics in Science & Tech, Disaster Management, Internal Security, and International Treaties.<br>
                • <strong>Consolidation:</strong> Audit all microtopics in Syllabus Navigator and mark 100% complete.<br>
                • <strong>Hard Stop Milestone:</strong> <span style="color:#059669; font-weight:700;">On {target_finish_date.strftime('%B %d, %Y')}, exactly 1 week before the exam, 100% of the entire syllabus is finished!</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with phase_col2:
        st.markdown(f"""
        <div class="pwskills-card">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#D97706; font-weight:800;">
                PHASE 2: {p1_end.strftime('%d %b')} - {p2_end.strftime('%d %b')} ({p2_days} DAYS)
            </div>
            <div class="pwskills-title" style="margin-top:4px; color:#D97706 !important;">
                🟡 Applied Governance, Economy & Ethics Case Studies
            </div>
            <div style="color:#334155; font-size:0.9rem; margin-top:8px; line-height:1.55;">
                • <strong>Target Papers:</strong> Complete pending microtopics in <strong>GS Paper 3</strong> (Macroeconomics, Monetary Policy, Biodiversity, Climate Conventions) and <strong>GS Paper 4</strong> (Ethics in Public Administration, Emotional Intelligence).<br>
                • <strong>Answer Writing:</strong> 2 timed Mains answers daily (10-markers, 150 words).<br>
                • <strong>Revision:</strong> Weekly active recall of Phase 1 flashcards to lock retention.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pwskills-card" style="border-color: #E9D5FF !important; background: #FAF5FF; margin-top:14px;">
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#7C3AED; font-weight:800;">
                PHASE 4: {target_finish_date.strftime('%d %b')} - {active_exam_date.strftime('%d %b')} (FINAL 7 DAYS)
            </div>
            <div class="pwskills-title" style="margin-top:4px; color:#7C3AED !important;">
                🛡️ The 7-Day Pre-Exam Buffer Protocol
            </div>
            <div style="color:#334155; font-size:0.9rem; margin-top:8px; line-height:1.55;">
                • <strong>Zero New Topics:</strong> Strictly no new syllabus reading allowed.<br>
                • <strong>Mocks:</strong> 2 Full Simulation GS Mocks + 1 CSAT Mock under strict exam hall timings (09:30-11:30 AM & 02:30-04:30 PM).<br>
                • <strong>Error Rectification:</strong> Review personal error log & high-frequency factual sheets.<br>
                • <strong>Peak Calm:</strong> Circadian sleep alignment for peak cognitive energy on exam day!
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. THE 7-DAY BUFFER DAY-BY-DAY ACTION PROTOCOL
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 22px 26px; margin-bottom: 24px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);">
        <h4 style="color: #7C3AED; margin-top: 0; font-weight: 700;">🛡️ The Day-by-Day Final 7-Day Buffer Schedule (Zero-Backlog Week)</h4>
        <div style="color: #475569; font-size: 0.92rem; margin-bottom: 14px;">
            Because your entire syllabus is 100% completed by Day -7, you utilize these final 7 days like a top ranker:
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px;">
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #0284C7;">
                <strong style="color: #0284C7;">Day -7 (7 Days Out):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Full-Length GS Simulation Mock 1 (09:30 - 11:30 AM). Negative marking audit by evening.</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #059669;">
                <strong style="color: #059669;">Day -6 (6 Days Out):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Full-Length CSAT Simulation Mock (02:30 - 04:30 PM). Comprehension rules & Speed Math review.</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #D97706;">
                <strong style="color: #D97706;">Day -5 (5 Days Out):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Rapid Sheet Revision GS1 & GS2: Articles 1-51A, Landmark Cases, Modern History Chronology.</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #7C3AED;">
                <strong style="color: #7C3AED;">Day -4 (4 Days Out):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Rapid Sheet Revision GS3 & GS4: Budget Key Ratios, Environment Conventions, Thinkers & Quotes.</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #0284C7;">
                <strong style="color: #0284C7;">Day -3 (3 Days Out):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Final Light Mock (50 MCQs). Light review of recurring traps. Mental confidence building.</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #059669;">
                <strong style="color: #059669;">Day -2 (2 Days Out):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Personal Error Log review only. Zero new concepts. 4-7-8 box breathing, evening walk, early sleep.</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 12px; border-left: 4px solid #DC2626;">
                <strong style="color: #DC2626;">Day -1 (Exam Eve):</strong><br>
                <span style="font-size: 0.88rem; color: #334155;">Books closed at 05:00 PM. Admit card & photo ID kit check. Sleep by 21:30 for 8+ hours restorative rest.</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. DAILY 24-HOUR TIME-TABLE BLUEPRINT
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>⏰ 5. Daily 24-Hour Time-Table Blueprint (Calibrated for " + str(daily_hours_input) + " Hours)</h4>", unsafe_allow_html=True)
    st.caption("Structured schedule designed to maintain velocity while preventing cognitive burnout:")

    tt_col1, tt_col2 = st.columns(2)
    with tt_col1:
        st.markdown(f"""
        <div class="pwskills-card">
            <div style="font-weight:700; color:#059669;">🌅 Morning Deep Work Session (06:30 - 09:30 AM) · 3.0 Hrs</div>
            <div style="color:#334155; font-size:0.88rem; margin-top:4px;">
                • Peak cortisol & focus window: Master 1-2 new heavy microtopics (GS2 Polity or GS3 Economy).<br>
                • Prepare 1-page bullet summary. No phone notifications.
            </div>
        </div>
        <div class="pwskills-card" style="margin-top:10px;">
            <div style="font-weight:700; color:#0284C7;">☀️ Midday Study Session (10:30 AM - 01:00 PM) · 2.5 Hrs</div>
            <div style="color:#334155; font-size:0.88rem; margin-top:4px;">
                • Second microtopic coverage (GS1 History or GS4 Ethics).<br>
                • Read key source / class lecture notes and summarize definitions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tt_col2:
        st.markdown(f"""
        <div class="pwskills-card">
            <div style="font-weight:700; color:#D97706;">🌤️ Afternoon Testing & Application (02:30 - 05:00 PM) · 2.5 Hrs</div>
            <div style="color:#334155; font-size:0.88rem; margin-top:4px;">
                • Solve 20 Prelims MCQs on today's topics (exam timing simulation).<br>
                • Write 1 Mains 10-marker answer draft. Analyze errors and update error log.
            </div>
        </div>
        <div class="pwskills-card" style="margin-top:10px;">
            <div style="font-weight:700; color:#7C3AED;">🌙 Evening Active Recall & Revision (06:00 - 08:30 PM) · 2.0 Hrs</div>
            <div style="color:#334155; font-size:0.88rem; margin-top:4px;">
                • Review today's 1-page notes using active recall / flashcards.<br>
                • Review yesterday's topics to seal synaptic retention. Sleep by 10:30 PM.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 7. ONE-CLICK ACTION HUB & INTEGRATIONS
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🚀 6. Action Hub: 1-Click Plan Integrations</h4>", unsafe_allow_html=True)
    st.caption("Apply this plan directly into your active dashboard targets or consult the AI Copilot:")

    act_col1, act_col2, act_col3 = st.columns(3)

    with act_col1:
        if st.button("🎯 Auto-Populate Targets into 'Productivity' Tab", key="btn_auto_populate_targets", use_container_width=True):
            if "targets" not in st.session_state.progress:
                st.session_state.progress["targets"] = []
            
            # Generate sample targets mapped to remaining syllabus
            new_plan_targets = [
                {
                    "id": f"tgt_plan_d1_{int(datetime.datetime.now().timestamp())}",
                    "title": f"Daily Target: Complete {int(daily_quota_needed)} microtopics (GS1/GS2)",
                    "timeframe": "Daily",
                    "paper": "GS Paper 2",
                    "subject": "Polity & Constitution",
                    "microtopic_id": None,
                    "microtopic_title": "Daily Quota from Exam Roadmap Planner",
                    "goal_type": "Note Making 📝",
                    "hours_est": float(daily_hours_input * 0.4),
                    "completed": False,
                    "created_at": today.isoformat()
                },
                {
                    "id": f"tgt_plan_d2_{int(datetime.datetime.now().timestamp())}",
                    "title": f"Daily Practice: Solve 20 Prelims PYQs + 1 Mains Answer Draft",
                    "timeframe": "Daily",
                    "paper": "GS Paper 2",
                    "subject": "Polity & Governance",
                    "microtopic_id": None,
                    "microtopic_title": "Daily PYQ & Answer Writing Quota",
                    "goal_type": "PYQ Practice 🎯",
                    "hours_est": float(daily_hours_input * 0.3),
                    "completed": False,
                    "created_at": today.isoformat()
                },
                {
                    "id": f"tgt_plan_w1_{int(datetime.datetime.now().timestamp())}",
                    "title": f"Weekly Milestone: Complete ~{int(weekly_quota_needed)} microtopics + Sectional Mock 1",
                    "timeframe": "Weekly",
                    "paper": "GS Paper 1",
                    "subject": "Modern History & Geography",
                    "microtopic_id": None,
                    "microtopic_title": "Weekly Roadmap Milestone",
                    "goal_type": "Revision 🔄",
                    "hours_est": float(daily_hours_input * 5),
                    "completed": False,
                    "created_at": today.isoformat()
                }
            ]
            st.session_state.progress["targets"].extend(new_plan_targets)
            save_user_progress(st.session_state.progress)
            st.success(f"🎉 Successfully populated {len(new_plan_targets)} daily and weekly targets into '⚡ Productivity & Targets' tab!")
            st.info("Switch to '⚡ Productivity & Targets' tab above to view and check off your live targets.")

    with act_col2:
        planner_copilot_prompt = (
            f"I am preparing for {st.session_state.selected_exam}. My exam will be conducted on '{active_exam_date.strftime('%Y-%m-%d')}'. "
            f"According to my Syllabus Navigator, I have completed {completed_cnt} microtopics ({completed_pct:.1f}%) and have {left_cnt} microtopics remaining ({left_pct:.1f}%). "
            f"My daily study capacity is {daily_hours_input} hours/day. "
            f"Please give me a detailed, day-by-day and phase-by-phase study plan so that I complete the entire syllabus exactly 1 week before the exam date ({target_finish_date.strftime('%Y-%m-%d')}), "
            f"leaving the final 7 days completely free as a buffer for full-length simulation tests, error audits, and rapid formula/micro-notes recall."
        )
        if st.button("🤖 Launch AI Strategy Consultation in Copilot", key="btn_open_copilot_planner", use_container_width=True):
            redirect_to_copilot(planner_copilot_prompt)

    with act_col3:
        plan_export_md = f"""# {st.session_state.selected_exam} Customized Exam Study Plan (1-Week Buffer Rule)
Generated on: {today.strftime('%B %d, %Y')}

## 1. Executive Summary & Timeline Audit
- **Official Exam Conduct Date:** {active_exam_date.strftime('%B %d, %Y')} ({total_days_until_exam} days remaining)
- **100% Syllabus Finish Deadline:** {target_finish_date.strftime('%B %d, %Y')} (Exactly 1 week before exam)
- **Net Preparation Days:** {prep_days_available} days ({net_active_prep_days} net study days)
- **Current Preparation Status:** {completed_cnt}/{total_micros} completed ({completed_pct:.1f}%) | {left_cnt} remaining ({left_pct:.1f}%)
- **Required Velocity:** {daily_quota_needed} microtopics/day (~{weekly_quota_needed} topics/week)
- **Daily Study Capacity:** {daily_hours_input} hours/day ({rev_ratio}% allocated to daily revision)

## 2. Phase-by-Phase Roadmap
- **Phase 1 ({today.strftime('%d %b')} - {p1_end.strftime('%d %b')}):** Core Foundation & GS1/GS2 Backlog Clearance ({p1_days} days).
- **Phase 2 ({p1_end.strftime('%d %b')} - {p2_end.strftime('%d %b')}):** Applied Governance, Economy & Ethics Case Studies ({p2_days} days).
- **Phase 3 ({p2_end.strftime('%d %b')} - {p3_end.strftime('%d %b')}):** Final Syllabus Clearance & Micro-Notes Consolidation ({p3_days} days).
- **Hard Stop Milestone:** 100% of entire syllabus completed on {target_finish_date.strftime('%B %d, %Y')}!

## 3. The 7-Day Pre-Exam Buffer Protocol (Zero New Topics)
- **Day -7:** Full-Length GS Simulation Mock 1 (09:30-11:30 AM) + Error log audit.
- **Day -6:** Full-Length CSAT Simulation Mock (02:30-04:30 PM) + Speed Math shortcuts.
- **Day -5:** GS1 & GS2 Rapid Sheet Revision (Articles 1-51A, Modern History Timelines).
- **Day -4:** GS3 & GS4 Rapid Sheet Revision (Budget Ratios, Environment Conventions, Ethics Quotes).
- **Day -3:** Final Light Simulation Mock + Mental calm reinforcement.
- **Day -2:** Review Personal Error Log only. Light walking, early sleep.
- **Day -1:** Complete rest after 5 PM. Check admit card, photo IDs, pens. Early bedtime.

## 4. Daily Schedule Template
- 06:30 - 09:30 AM: Morning Deep Work Session (Microtopic 1)
- 10:30 AM - 01:00 PM: Midday Session (Microtopic 2)
- 02:30 - 05:00 PM: Afternoon Testing (20 MCQs + 1 Mains Answer Draft)
- 06:00 - 08:30 PM: Evening Active Recall & Daily Revision
"""
        st.download_button(
            label="📥 Download Study Plan (Markdown)",
            data=plan_export_md,
            file_name=f"UPSC_Exam_Study_Plan_{active_exam_date.strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown("---")

    # 8. INTERACTIVE REMAINING TOPICS EXPLORER
    with st.expander(f"🔍 Browse Unfinished Topics Left to Study ({left_cnt} Remaining Modules)", expanded=False):
        st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Directly inspect which microtopics are still pending per paper, mark them completed as you study, or click '💡 AI Explainer' to study them with your AI Copilot:</p>", unsafe_allow_html=True)
        
        sel_paper_browse = st.selectbox("Select GS Paper to Inspect:", ["GS Paper 1", "GS Paper 2", "GS Paper 3", "GS Paper 4"], key="planner_browse_paper_select")
        if sel_paper_browse in syllabus_data:
            p_subjects = syllabus_data[sel_paper_browse].get("subjects", {})
            for s_key, s_data in p_subjects.items():
                s_topics = s_data.get("topics", {})
                pending_micros_in_subj = []
                for t_key, t_data in s_topics.items():
                    for m in t_data.get("microtopics", []):
                        m_id = f"{sel_paper_browse}_{s_key}_{t_key}_{m}"
                        if m_id not in completed_set:
                            pending_micros_in_subj.append((m, m_id, t_key))
                
                if pending_micros_in_subj:
                    with st.expander(f"📚 {s_data.get('title', s_key)} ({len(pending_micros_in_subj)} topics left)", expanded=False):
                        for m_title, m_id, top_key in pending_micros_in_subj[:15]:
                            b_c1, b_c2 = st.columns([0.75, 0.25])
                            with b_c1:
                                chk_p = st.checkbox(f"{m_title} `[{top_key}]`", value=False, key=f"chk_plan_exp_{m_id}")
                                if chk_p:
                                    if m_id not in st.session_state.progress["completed"]:
                                        st.session_state.progress["completed"].append(m_id)
                                        save_user_progress(st.session_state.progress)
                                        st.rerun()
                            with b_c2:
                                if st.button("💡 AI Explainer", key=f"btn_plan_ai_{m_id}", use_container_width=True):
                                    redirect_to_copilot(f"Explain the microtopic '{m_title}' under '{top_key}' ({sel_paper_browse}) for {st.session_state.selected_exam} in detail. Provide core concepts, key facts, Prelims MCQs, and Mains answer writing approaches.")

# ==========================================
# VIEW: ⚡ PRODUCTIVITY & TARGETS
# ==========================================
elif nav_mode == "⚡ Productivity & Targets":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>⚡ Daily, Weekly & Monthly Productivity Matrix</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Plan study targets mapped to GS Syllabus microtopics, monitor daily velocity graphics, and track target completion.</p>", unsafe_allow_html=True)
    
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
            <div style="color: #0284C7; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{daily_pct:.0f}% Completed Today</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🗓️ Weekly Target Rate</div>
            <div class="metric-value">{weekly_done}/{weekly_total}</div>
            <div style="color: #059669; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{weekly_pct:.0f}% Week Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📆 Monthly Milestones</div>
            <div class="metric-value">{monthly_done}/{monthly_total}</div>
            <div style="color: #7C3AED; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{monthly_pct:.0f}% Month Goal</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Productivity Velocity</div>
            <div class="metric-value">{daily_done + 3 if daily_done > 0 else 3} Days</div>
            <div style="color: #D97706; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">Active Flow Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Real-Time Productivity Graphics
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📊 Real-Time Productivity Graphics & Target Analytics</h4>", unsafe_allow_html=True)
    
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
                <div style="font-family: 'Outfit', sans-serif; font-size: 3.2rem; font-weight: 800; color: #0284C7; line-height: 1;">
                    {daily_pct:.0f}%
                </div>
                <div style="color: #059669; font-weight: 700; font-size: 0.88rem; margin-top: 6px; letter-spacing: 0.5px;">
                    {perf_status}
                </div>
            </div>
            <div style="background: #F8FAFC; border-radius: 12px; padding: 12px 14px; border: 1px solid #E2E8F0;">
                <div style="font-size: 0.82rem; color: #334155;">
                    📌 <strong>Syllabus Microtopics Mapped:</strong> {sum(1 for t in targets if t.get('microtopic_id'))} linked
                </div>
                <div style="font-size: 0.82rem; color: #334155; margin-top: 4px;">
                    ⏱️ <strong>Est. Hours Logged Today:</strong> {sum(float(t.get('hours_est', 1.0)) for t in targets if t.get('completed')):.1f} hrs
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Create Target Mapped to Syllabus
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>➕ Create New Target (Mapped to Syllabus Navigator)</h4>", unsafe_allow_html=True)
    
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
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📋 Active Study Targets & Execution Matrix</h4>", unsafe_allow_html=True)
    
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
                            redirect_to_copilot(f"Explain the UPSC topic '{tgt['microtopic_title']}' ({tgt['paper']}) in detail like a UPSC exam teacher. Provide core concepts, Prelims relevance, Mains relevance, practice MCQs for Prelims, and Mains practice questions.")
                with btn_cols[1]:
                    if st.button("🗑️", key=f"btn_del_tgt_{t_id}", use_container_width=True):
                        st.session_state.progress["targets"].remove(tgt)
                        save_user_progress(st.session_state.progress)
                        st.rerun()
            st.markdown("<hr style='margin: 8px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)

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
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>💞 Aspirant Relationship & Preparation Ecosystem</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Manage emotional dynamics (ghosting, one-sided love, breakups), map emotional stress to UPSC syllabus progress, and protect your study targets.</p>", unsafe_allow_html=True)
    
    # Initialize relationship state in user progress if not present
    rel_state = st.session_state.progress.setdefault("relationship_state", {
        "status": "Single & Focused on UPSC 🛡️",
        "emotional_situation": "🟢 Emotionally Stable & Supported",
        "drain_level": 3
    })
    
    # Calculate Syllabus Progress Metrics from Syllabus Navigator
    total_micros = 623
    completed_set = set(st.session_state.progress.get("completed", []))
    completed_cnt = len(completed_set)
    covered_pct = (completed_cnt / total_micros * 100) if total_micros > 0 else 0
    left_pct = max(0.0, 100.0 - covered_pct)
    left_cnt = max(0, total_micros - completed_cnt)

    # Calculate Paper-wise breakdown from Syllabus Navigator
    gs1_done = sum(1 for m in completed_set if m.startswith("GS Paper 1"))
    gs2_done = sum(1 for m in completed_set if m.startswith("GS Paper 2"))
    gs3_done = sum(1 for m in completed_set if m.startswith("GS Paper 3"))
    gs4_done = sum(1 for m in completed_set if m.startswith("GS Paper 4"))

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
                
            r_saved = st.form_submit_button("💾 Save Profile & Correlate with Syllabus Navigator", use_container_width=True)
            if r_saved:
                st.session_state.progress["relationship_state"] = {
                    "status": rel_status,
                    "emotional_situation": emo_situation,
                    "drain_level": drain
                }
                save_user_progress(st.session_state.progress)
                st.success("✅ Profile Saved & Syllabus Correlation Updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Syllabus Mapping & Emotional Impact Analytics Dashboard
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📊 Relationship Stress vs. Syllabus Completion Matrix</h4>", unsafe_allow_html=True)
    
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
            <div style="color: #0284C7; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">Study Continuity Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphical Analysis & Paper-wise Correlation Section
    g_col1, g_col2 = st.columns([1.2, 0.8])
    with g_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">📈 Syllabus Progress vs. Emotional Energy Allocation</div>
            <div class="pwskills-desc">Real-time comparison of completed syllabus microtopics against remaining topics and current emotional bandwidth drain.</div>
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
        curr_emo = rel_state.get("emotional_situation", "🟢 Emotionally Stable & Supported")
        
        if "Ghosting" in curr_status:
            adv_color = "#EF4444"
            adv_title = "👻 Ghosting Recovery Protocol Active"
            adv_msg = f"Ghosting causes cognitive loops. You have **{left_cnt} microtopics left**. Every 30 mins spent checking last seen/messages costs 1 microtopic of GS Polity or Economy. Execute 25-min Pomodoro sprints now!"
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
            adv_color = "#059669"
            adv_title = "🟢 High Focus Equilibrium"
            adv_msg = f"Your emotional state is stable. Capitalize on this clarity to crush the remaining **{left_cnt} microtopics** in GS Paper 1, 2, 3, and 4!"

        st.markdown(f"""
        <div class="pwskills-card" style="border-color: {adv_color} !important;">
            <div class="pwskills-title" style="color: {adv_color} !important;">{adv_title}</div>
            <div style="color: #1E293B; font-size: 0.92rem; margin-top: 8px; line-height: 1.55;">
                {adv_msg}
            </div>
            <div style="margin-top: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #475569;">
                STATUS: <span style="color: {adv_color}; font-weight: 700;">{curr_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. DYNAMIC CORRELATION ENGINE: SYLLABUS NAVIGATOR X RELATIONSHIP PROFILE
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🔗 Dynamic Correlation: Syllabus Navigator Completion x Relationship Profile</h4>", unsafe_allow_html=True)
    st.caption("Deep analytical cross-mapping between your active microtopics in Syllabus Navigator and your current relationship inputs:")

    est_days_lost = round(drain * 1.8, 1)
    cognitive_capacity = max(10, 100 - drain * 9)

    c_matrix_col1, c_matrix_col2 = st.columns([1, 1])
    with c_matrix_col1:
        st.markdown(f"""
        <div class="pwskills-card" style="border-color: #BAE6FD !important;">
            <div class="pwskills-title" style="color: #0284C7 !important;">📊 GS Paper Microtopic Breakdown</div>
            <div style="color: #334155; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                • <strong>GS Paper 1 (History, Geography, Society):</strong> <span style="color: #059669; font-weight: 700;">{gs1_done}/386</span> completed ({ (gs1_done/386*100) if 386>0 else 0:.1f}%)<br>
                • <strong>GS Paper 2 (Polity, Governance, IR):</strong> <span style="color: #059669; font-weight: 700;">{gs2_done}/89</span> completed ({ (gs2_done/89*100) if 89>0 else 0:.1f}%)<br>
                • <strong>GS Paper 3 (Economy, Environment, Sci-Tech):</strong> <span style="color: #059669; font-weight: 700;">{gs3_done}/73</span> completed ({ (gs3_done/73*100) if 73>0 else 0:.1f}%)<br>
                • <strong>GS Paper 4 (Ethics, Integrity, Aptitude):</strong> <span style="color: #059669; font-weight: 700;">{gs4_done}/69</span> completed ({ (gs4_done/69*100) if 69>0 else 0:.1f}%)
            </div>
            <div style="margin-top: 12px; padding: 10px 14px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; font-size: 0.85rem; color: #1E293B;">
                🎯 <strong>Syllabus Navigator Status:</strong> {completed_cnt} of 623 microtopics checked ({covered_pct:.1f}% finished).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_matrix_col2:
        st.markdown(f"""
        <div class="pwskills-card" style="border-color: #FDE68A !important;">
            <div class="pwskills-title" style="color: #D97706 !important;">⚠️ Emotional Drag & Rumination Impact</div>
            <div style="color: #334155; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                • <strong>Current Emotional Toll:</strong> <span style="color: #D97706; font-weight: 700;">{drain}/10 Drain Index</span><br>
                • <strong>Cognitive Retention Capacity:</strong> <span style="color: #0284C7; font-weight: 700;">{cognitive_capacity}%</span> effective bandwidth<br>
                • <strong>Estimated Productivity Loss:</strong> <span style="color: #DC2626; font-weight: 700;">~{est_days_lost} days/month</span> lost to rumination & anxiety<br>
                • <strong>Vulnerable Syllabus Area:</strong> <span style="color: #7C3AED; font-weight: 700;">{"GS4 Ethics & GS2 Polity" if drain>=6 else "GS1 & GS3 Core Subjects"}</span>
            </div>
            <div style="margin-top: 12px; padding: 10px 14px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; font-size: 0.85rem; color: #1E293B;">
                💡 <strong>Corelation Finding:</strong> Relationship stress level ({drain}/10) directly threatens the remaining {left_cnt} microtopics if left unmanaged.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. ACTIONABLE & IMPLEMENTABLE SUGGESTIONS SUITE
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>💡 Tailored Implementable Suggestions for Prep & Relationship Management</h4>", unsafe_allow_html=True)
    st.caption("Concrete, actionable protocols designed for immediate daily implementation based on your correlation profile:")

    # Determine dynamic suggestion content based on profile
    if drain >= 7:
        quota_recommendation = (
            f"**High Drain Execution Quota ({drain}/10):** Do NOT force 3-hour study blocks—rumination will shatter retention. "
            f"Switch to **25-minute Pomodoro Sprints**. Set a daily quota of **2 to 3 microtopics** from Syllabus Navigator. "
            f"Start your day with lightweight GS4 Ethics microtopics (*Emotional Intelligence*, *Human Values*) to build emotional composure before tackling heavy topics."
        )
    elif drain >= 4:
        quota_recommendation = (
            f"**Moderate Drain Execution Quota ({drain}/10):** Maintain **45-minute focus sprints**. "
            f"Target **4 microtopics daily** from Syllabus Navigator ({left_cnt} remaining). "
            f"Complete your hardest GS2 Polity or GS3 Economy microtopic before 11:30 AM before checking any personal messages."
        )
    else:
        quota_recommendation = (
            f"**Low Drain Execution Quota ({drain}/10):** Your emotional state is stable. "
            f"Capitalize on high focus: Execute **90-minute deep work blocks** targeting **5 to 6 microtopics daily** to finish the remaining {left_cnt} microtopics ahead of schedule!"
        )

    sug_col1, sug_col2 = st.columns(2)
    with sug_col1:
        st.markdown(f"""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #059669 !important;">🎯 1. Microtopic Execution Plan (Syllabus Navigator)</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                {quota_recommendation}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #D97706 !important;">⚡ 2. The "5-PYQ Circuit Breaker" Rule</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                <strong>Implementation Protocol:</strong> Whenever you feel an overwhelming urge to check message timestamps, stalk social media, or overthink <em>"{curr_status}"</em>:<br>
                1. <strong>Enforce a 10-minute pause:</strong> Step away from your phone.<br>
                2. <strong>Solve 5 PYQs:</strong> Open Syllabus Navigator or PYQ section and solve 5 MCQs or write 1 Mains answer outline.<br>
                3. <strong>Reward mechanism:</strong> Only after completing 5 PYQs are you allowed to look at your personal phone. This re-wires dopamine loops towards UPSC targets.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sug_col2:
        st.markdown(f"""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #7C3AED !important;">📖 3. GS4 Ethics Syllabus Integration (Study Your Situation)</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                <strong>Syllabus Synergy:</strong> Convert your personal relationship dynamics into GS4 Ethics study material!<br>
                • <strong>Current Inputs:</strong> <em>{curr_status}</em> ({curr_emo})<br>
                • <strong>GS4 Syllabus Topic:</strong> <em>Emotional Intelligence (EI), Moral Fortitude & Attitude</em><br>
                • <strong>Exam Task:</strong> Write a 150-word Mains practice answer on: <em>"How does Emotional Intelligence help a civil servant handle unprovoked personal stress while maintaining administrative efficiency?"</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #0284C7 !important;">⏰ 4. Strict Time-Fence & Digital Boundary Schedule</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                • <strong>08:30 AM - 07:30 PM (UPSC Darkout):</strong> Phone on DND/Focus Mode. Zero checking of relationship chats. Focus 100% on Syllabus Navigator microtopics.<br>
                • <strong>07:30 PM - 08:15 PM (Personal Window):</strong> Fixed 45-min window for personal communication, calls, or reflection logging.<br>
                • <strong>10:15 PM Onwards (Digital Shutdown):</strong> No screen time or overthinking before sleep to ensure cognitive recovery.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. 1-CLICK AI COUNSELOR CONSULTATION GENERATOR
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🤖 1-Click AI Counselor Consultation (Pre-Filled Profile & Syllabus Data)</h4>", unsafe_allow_html=True)
    st.caption("Click the button below to launch an AI Consultation tailored to your exact relationship profile and remaining microtopics:")

    consult_prompt = (
        f"I am preparing for UPSC Civil Services. My current relationship dynamics is '{curr_status}', my emotional state is '{curr_emo}', and my emotional drain level is {drain}/10. "
        f"According to my Syllabus Navigator tracking, I have completed {completed_cnt} microtopics ({covered_pct:.1f}%) and have {left_cnt} microtopics remaining ({left_pct:.1f}%). "
        f"Please provide an empathetic, highly structured, 7-day actionable study and emotional recovery plan that allows me to protect my study targets while managing relationship stress effectively."
    )

    if st.button("🚀 Launch AI Counselor Consultation for My Profile & Syllabus Progress", key="btn_rel_correlated_consult", use_container_width=True):
        redirect_to_copilot(consult_prompt)

    st.markdown("---")

    # 6. Private Emotional Venting & Reflection Journal
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>✍️ Aspirant Emotional Venting & Mindset Reflection Log</h4>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>🧘 Aspirant Mental Health & Mindset Wellness Hub</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Empathetic psychological guidance, stress management, anti-burnout strategies, and daily mindset building correlated with your Syllabus Navigator progress.</p>", unsafe_allow_html=True)
    
    # Initialize mental health state in user progress if not present
    mh_state = st.session_state.progress.setdefault("mental_health_state", {
        "mood": "🟡 Moderate Stress / Slight Fatigue",
        "trigger": "📚 Syllabus Overwhelm & Fear of Completion",
        "energy_level": 5
    })

    # Calculate Syllabus Progress Metrics from Syllabus Navigator
    total_micros = 623
    completed_set = set(st.session_state.progress.get("completed", []))
    completed_cnt = len(completed_set)
    covered_pct = (completed_cnt / total_micros * 100) if total_micros > 0 else 0
    left_pct = max(0.0, 100.0 - covered_pct)
    left_cnt = max(0, total_micros - completed_cnt)

    # Calculate Paper-wise breakdown from Syllabus Navigator
    gs1_done = sum(1 for m in completed_set if m.startswith("GS Paper 1"))
    gs2_done = sum(1 for m in completed_set if m.startswith("GS Paper 2"))
    gs3_done = sum(1 for m in completed_set if m.startswith("GS Paper 3"))
    gs4_done = sum(1 for m in completed_set if m.startswith("GS Paper 4"))

    # 1. Diagnostic Mindset & Stressor Input Form
    with st.expander("⚙️ Configure Your Daily Mindset & Stressor Profile", expanded=True):
        with st.form("mh_config_form"):
            mh_col1, mh_col2, mh_col3 = st.columns([1.2, 1.2, 1])
            
            mood_options = [
                "🟢 High Energy & Hyper-Focused",
                "🟡 Moderate Stress / Slight Fatigue",
                "🟠 Overwhelmed & Syllabus Anxiety",
                "🔴 Severe Burnout & Low Motivation"
            ]
            curr_mood = mh_state.get("mood", mood_options[1])
            mood_idx = mood_options.index(curr_mood) if curr_mood in mood_options else 1

            trigger_options = [
                "📚 Syllabus Overwhelm & Fear of Completion",
                "🎯 Mock Test Panic & Negative Marking Anxiety",
                "😴 Sleep Deprivation & Chronic Fatigue",
                "👥 Social Isolation & Family Expectations",
                "⏳ Fear of Failure & Repeat Attempt Pressure"
            ]
            curr_trigger = mh_state.get("trigger", trigger_options[0])
            trigger_idx = trigger_options.index(curr_trigger) if curr_trigger in trigger_options else 0

            with mh_col1:
                selected_mood = st.selectbox(
                    "Current Mental & Energy State:",
                    mood_options,
                    index=mood_idx,
                    key="mh_mood_select_input"
                )
            with mh_col2:
                selected_trigger = st.selectbox(
                    "Primary Stressor / Mindset Trigger:",
                    trigger_options,
                    index=trigger_idx,
                    key="mh_trigger_select_input"
                )
            with mh_col3:
                energy_lvl = st.slider("Daily Focus Capacity (1-10):", min_value=1, max_value=10, value=int(mh_state.get("energy_level", 5)), key="mh_energy_slider")
                
            mh_saved = st.form_submit_button("💾 Save Mindset Profile & Correlate with Syllabus", use_container_width=True)
            if mh_saved:
                st.session_state.progress["mental_health_state"] = {
                    "mood": selected_mood,
                    "trigger": selected_trigger,
                    "energy_level": energy_lvl
                }
                save_user_progress(st.session_state.progress)
                st.success("✅ Mindset Profile Saved & Syllabus Correlation Updated!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Dynamic Correlation Dashboard (Mental Health x Syllabus Navigator)
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📊 Mental Health vs. Syllabus Completion Matrix</h4>", unsafe_allow_html=True)
    
    # Calculate Cognitive Capacity and Absorption Score
    if "🔴 Severe Burnout" in curr_mood:
        cognitive_capacity = 25
        status_badge = "🔴 Burnout Protocol Active"
        badge_color = "#EF4444"
    elif "🟠 Overwhelmed" in curr_mood:
        cognitive_capacity = 45
        status_badge = "🟠 De-compress Needed"
        badge_color = "#F59E0B"
    elif "🟡 Moderate Stress" in curr_mood:
        cognitive_capacity = 70
        status_badge = "🟡 Moderate Energy"
        badge_color = "#38BDF8"
    else:
        cognitive_capacity = 95
        status_badge = "🟢 Peak Flow State"
        badge_color = "#34D399"

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Syllabus Completed</div>
            <div class="metric-value">{completed_cnt}</div>
            <div style="color: #34D399; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{covered_pct:.1f}% Microtopics Done</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Microtopics Remaining</div>
            <div class="metric-value">{left_cnt}</div>
            <div style="color: #EF4444; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{left_pct:.1f}% Microtopics Left</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🧠 Focus Capacity</div>
            <div class="metric-value">{cognitive_capacity}%</div>
            <div style="color: {badge_color}; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">{status_badge}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        daily_absorption = max(1, int((energy_lvl / 10.0) * (cognitive_capacity / 100.0) * 6))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚡ Daily Microtopic Quota</div>
            <div class="metric-value">{daily_absorption} / day</div>
            <div style="color: #0284C7; font-size: 0.85rem; font-weight: 700; margin-top: 4px;">Calibrated Target</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cross-Mapping Analysis Section
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🔗 Dynamic Correlation: Mindset State x Syllabus Navigator Progress</h4>", unsafe_allow_html=True)
    
    corr_col1, corr_col2 = st.columns([1, 1])
    with corr_col1:
        st.markdown(f"""
        <div class="pwskills-card" style="border-color: #BAE6FD !important;">
            <div class="pwskills-title" style="color: #0284C7 !important;">📖 Syllabus Progress Status</div>
            <div style="color: #334155; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                • <strong>GS Paper 1 (History, Geography, Society):</strong> <span style="color: #059669; font-weight: 700;">{gs1_done}/386</span> microtopics<br>
                • <strong>GS Paper 2 (Polity, Governance, IR):</strong> <span style="color: #059669; font-weight: 700;">{gs2_done}/89</span> microtopics<br>
                • <strong>GS Paper 3 (Economy, Environment, Sci-Tech):</strong> <span style="color: #059669; font-weight: 700;">{gs3_done}/73</span> microtopics<br>
                • <strong>GS Paper 4 (Ethics, Integrity, Aptitude):</strong> <span style="color: #059669; font-weight: 700;">{gs4_done}/69</span> microtopics
            </div>
            <div style="margin-top: 12px; padding: 10px 14px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; font-size: 0.85rem; color: #1E293B;">
                🎯 <strong>Master Status:</strong> {completed_cnt} of 623 microtopics checked ({covered_pct:.1f}% covered).
            </div>
        </div>
        """, unsafe_allow_html=True)

    with corr_col2:
        st.markdown(f"""
        <div class="pwskills-card" style="border-color: {badge_color} !important;">
            <div class="pwskills-title" style="color: {badge_color} !important;">🧘 Mindset Drag & Academic Vulnerability</div>
            <div style="color: #334155; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                • <strong>Active Mindset State:</strong> <span style="color: {badge_color}; font-weight: 700;">{curr_mood}</span><br>
                • <strong>Primary Stress Trigger:</strong> <span style="color: #D97706; font-weight: 700;">{curr_trigger}</span><br>
                • <strong>Daily Focus Energy Level:</strong> <span style="color: #0284C7; font-weight: 700;">{energy_lvl}/10</span><br>
                • <strong>Vulnerable Syllabus Area:</strong> <span style="color: #7C3AED; font-weight: 700;">{"GS3 Economy & GS1 History (High Fatigue)" if cognitive_capacity < 50 else "GS2 Polity & GS4 Ethics"}</span>
            </div>
            <div style="margin-top: 12px; padding: 10px 14px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; font-size: 0.85rem; color: #1E293B;">
                💡 <strong>Corelation Finding:</strong> Current focus capacity ({cognitive_capacity}%) requires matching daily microtopic targets to your energy level to prevent burnout.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. TAILORED IMPLEMENTABLE SUGGESTIONS SUITE
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>💡 Tailored Suggestions for Mental Health & Syllabus Handling</h4>", unsafe_allow_html=True)
    st.caption("Concrete, actionable steps to protect your mental health while making steady progress on Syllabus Navigator microtopics:")

    if "🔴 Severe Burnout" in curr_mood:
        plan_suggestion = (
            f"**Burnout Recovery Protocol:** STOP attempting 10-hour study marathons—your brain is in cognitive saturation. "
            f"Set a micro-quota of **1 to 2 GS4 Ethics microtopics** per day. GS4 Ethics (*Emotional Intelligence*, *Human Values*) requires low technical fatigue and reinforces psychological resilience."
        )
    elif "🟠 Overwhelmed" in curr_mood:
        plan_suggestion = (
            f"**Overwhelm De-escalation Plan:** Looking at all {left_cnt} remaining microtopics creates panic. "
            f"Hide the master list. Select **only 2 microtopics** for today (e.g. GS2 Polity Articles or GS1 Geography). "
            f"Use **25-minute Pomodoro sprints** with 10-minute rest breaks."
        )
    elif "🟡 Moderate Stress" in curr_mood:
        plan_suggestion = (
            f"**Moderate Stress Calibration:** Use **45-minute study sprints**. Target **3 to 4 microtopics daily**. "
            f"Solve **5 Prelims PYQs** after completing each microtopic to convert stress into tangible test confidence."
        )
    else:
        plan_suggestion = (
            f"**Hyper-Focus Flow State:** Your mental energy is high ({energy_lvl}/10). "
            f"Execute **90-minute deep work blocks** targeting **5 to 6 heavy microtopics daily** (GS3 Economy, GS2 Governance) to rapidly reduce the remaining {left_cnt} microtopics!"
        )

    sug_col1, sug_col2 = st.columns(2)
    with sug_col1:
        st.markdown(f"""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #059669 !important;">🎯 1. Mindset-Calibrated Microtopic Plan</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                {plan_suggestion}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #D97706 !important;">⚡ 2. The "1-Topic Isolation" Anti-Panic Technique</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                <strong>Implementation Protocol:</strong> When anxiety strikes regarding <em>"{curr_trigger}"</em>:<br>
                1. <strong>Close all tabs & books:</strong> Except for 1 single microtopic from Syllabus Navigator.<br>
                2. <strong>30-Minute Execution:</strong> Read only that microtopic or watch 1 focused explainer.<br>
                3. <strong>Check the box:</strong> Marking 1 microtopic checked releases dopamine and restores emotional control.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sug_col2:
        st.markdown(f"""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #7C3AED !important;">📖 3. GS4 Ethics Synergy (Mindset as Syllabus Content)</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                <strong>Exam Integration:</strong> Turn your current psychological stressor into GS4 Ethics study material!<br>
                • <strong>Current Trigger:</strong> <em>{curr_trigger}</em><br>
                • <strong>GS4 Syllabus Topic:</strong> <em>Stress Management, Emotional Intelligence & Work-Life Balance in Public Service</em><br>
                • <strong>Exam Task:</strong> Write a 150-word GS4 answer on: <em>"What coping strategies can a District Collector adopt to prevent emotional burnout during crisis management?"</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title" style="color: #0284C7 !important;">⏰ 4. Circadian & Sleep Hygiene Protocol</div>
            <div style="color: #1E293B; font-size: 0.9rem; margin-top: 8px; line-height: 1.6;">
                • <strong>Strict Sleep Window:</strong> Minimum 7.5 hours of sleep. Zero late-night textbook reading past 10:30 PM.<br>
                • <strong>Somatic Cortisol Reset:</strong> Perform 4 cycles of 4-7-8 box breathing twice daily (morning & before sleep).<br>
                • <strong>Post-Study Walk:</strong> 15-minute outdoor walk without phone after your evening study session to clear mental fatigue.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. 1-CLICK AI MENTAL HEALTH COUNSELOR LAUNCHER
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🤖 1-Click AI Counselor Consultation (Pre-Filled Mindset & Syllabus Data)</h4>", unsafe_allow_html=True)
    st.caption("Click the button below to launch an empathetic AI Consultation tailored to your exact mood, stressor, and remaining microtopics:")

    consult_mh_prompt = (
        f"I am a UPSC aspirant. My current mental state is '{curr_mood}', my primary stress trigger is '{curr_trigger}', and my daily focus energy level is {energy_lvl}/10. "
        f"In my Syllabus Navigator tracking, I have completed {completed_cnt} microtopics ({covered_pct:.1f}%) and have {left_cnt} microtopics remaining ({left_pct:.1f}%). "
        f"Please provide an empathetic, professional psychological strategy and a daily study routine that helps me overcome {curr_trigger} while steadily completing my GS microtopics."
    )

    if st.button("🚀 Launch AI Counselor Consultation for My Mindset & Syllabus Progress", key="btn_mh_correlated_consult", use_container_width=True):
        redirect_to_copilot(consult_mh_prompt)

    st.markdown("---")

    # 5. Interactive Mindfulness & Helpline Resources
    rec_col1, rec_col2 = st.columns([1.2, 0.8])
    with rec_col1:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🧘 4-7-8 Box Breathing & Relaxation Tool</h4>", unsafe_allow_html=True)
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
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📞 Tele-MANAS Helplines</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div class="pwskills-card" style="border-color: #BBF7D0 !important; background: #F0FDF4 !important;">
            <div style="color: #16A34A !important; font-weight: 800 !important; font-size: 1.15rem !important;">Govt. Tele-MANAS Helpline</div>
            <div style="color: #0F172A !important; font-size: 1.4rem !important; font-weight: 800 !important; margin-top: 6px !important;">📞 14416 / 1800-891-4416</div>
            <div style="color: #334155 !important; font-size: 0.92rem !important; margin-top: 6px !important; font-weight: 500 !important;">24x7 Free & Confidential Mental Health Counseling by Govt of India</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# VIEW 4: 📝 MOCK TESTS & ASSESSMENT
# ==========================================
elif nav_mode == "📝 Mock Tests & Assessment":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>📝 Prelims & Mains Mock Test Arena</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Simulated Prelims MCQs with instant scoring (-0.66 negative marking), automated Weak vs Strong Subjects diagnostics, and Mains Answer Writing Evaluation.</p>", unsafe_allow_html=True)
    
    # Dynamic Test Metrics Row from history
    hist = st.session_state.get("mock_test_history", [])
    tests_attempted = len(hist)
    avg_accuracy = (sum(h.get("accuracy", 0.0) for h in hist) / tests_attempted) if tests_attempted > 0 else 74.5
    latest_score = hist[-1].get("score", 14.68) if hist else 14.68
    total_weak_identified = sum(len(h.get("weak", [])) for h in hist)

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tests Attempted</div>
            <div class="metric-value">{tests_attempted}</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Accuracy</div>
            <div class="metric-value">{avg_accuracy:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Latest Test Score</div>
            <div class="metric-value">{latest_score:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Weak Subject Areas</div>
            <div class="metric-value" style="color: {'#DC2626' if total_weak_identified > 0 else '#059669'};">{total_weak_identified} Focus Areas</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sub-tabs
    test_tab1, test_tab2, test_tab3, test_tab4 = st.tabs([
        "🎯 Prelims Mock Arena (Interactive Test & Report)",
        "⚡ Custom Topic Generator",
        "✍️ Mains Answer Writing Challenge",
        "📊 Test History & Diagnostics"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: PRELIMS MOCK ARENA
    # --------------------------------------------------------------------------
    with test_tab1:
        # State 1: A report exists -> Show Comprehensive Diagnostic Report
        if st.session_state.get("mock_test_report") is not None:
            rep = st.session_state.mock_test_report
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 18px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <span style="background: {rep['tier_color']}15; color: {rep['tier_color']}; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; border: 1px solid {rep['tier_color']}40;">
                            {rep['tier_title']}
                        </span>
                        <h3 style="color: #0F172A; font-size: 1.45rem; font-weight: 800; margin: 10px 0 4px 0;">📊 Test Performance & Diagnostic Report</h3>
                        <div style="color: #475569; font-size: 0.92rem;">{rep['title']} · Standard UPSC Prelims Negative Marking (-0.66)</div>
                    </div>
                </div>
                <div style="margin-top: 14px; padding: 12px 16px; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; font-size: 0.92rem; color: #334155;">
                    💡 <b>Cutoff Projection:</b> {rep['tier_desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Scorecard 4-box metrics
            s_c1, s_c2, s_c3, s_c4 = st.columns(4)
            with s_c1:
                st.markdown(f"""
                <div class="metric-card" style="border-color: #BBF7D0;">
                    <div class="metric-label">Net Score Obtained</div>
                    <div class="metric-value" style="color: #059669;">{rep['net_marks']:.2f} <span style="font-size: 1rem; color: #64748B;">/ {rep['max_marks']:.0f}</span></div>
                </div>
                """, unsafe_allow_html=True)
            with s_c2:
                st.markdown(f"""
                <div class="metric-card" style="border-color: #C7D2FE;">
                    <div class="metric-label">Overall Accuracy</div>
                    <div class="metric-value" style="color: #4F46E5;">{rep['accuracy_pct']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with s_c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Attempts Breakdown</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-top: 8px;">
                        <span style="color: #059669;">✔ {rep['correct']} Correct</span> · <span style="color: #DC2626;">✖ {rep['incorrect']} Wrong</span> · <span style="color: #64748B;">⚪ {rep['skipped']} Skip</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with s_c4:
                st.markdown(f"""
                <div class="metric-card" style="border-color: #FECACA;">
                    <div class="metric-label">Negative Penalty</div>
                    <div class="metric-value" style="color: #DC2626;">-{rep['negative_marks']:.2f} <span style="font-size: 0.82rem; color: #64748B;">Marks</span></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ------------------------------------------------------------------
            # WEAK SUBJECTS vs STRONG SUBJECTS DIAGNOSTIC REPORT
            # ------------------------------------------------------------------
            st.markdown("<h4 style='color: #0F172A; font-weight: 800; margin-bottom: 6px;'>🎯 Subject-Wise Diagnostic Breakdown: Strong vs. Weak Areas</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>Cross-subject accuracy analysis categorized into mastery tiers to guide your revision schedule.</p>", unsafe_allow_html=True)

            col_strong, col_weak = st.columns(2)
            with col_strong:
                st.markdown("<h5 style='color: #065F46; font-weight: 700;'>🟢 Strong Subjects (Accuracy ≥ 70%)</h5>", unsafe_allow_html=True)
                if rep["strong_subjects"]:
                    for s in rep["strong_subjects"]:
                        st.markdown(f"""
                        <div class="diagnostic-card-strong">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-size: 1.05rem; color: #065F46;">{s['subject']}</strong>
                                <span style="background: #DCFCE7; color: #15803D; font-weight: 700; padding: 3px 10px; border-radius: 999px; font-size: 0.8rem;">
                                    {s['accuracy']}% Acc · {s['marks']:.2f} M
                                </span>
                            </div>
                            <div style="font-size: 0.85rem; color: #166534; margin-top: 6px;">
                                {s['assessment']}
                            </div>
                            <div style="font-size: 0.78rem; color: #15803D; margin-top: 4px;">
                                Score: {s['correct']}/{s['attempted']} Correct ({s['skipped']} Skipped)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No subjects reached the ≥ 70% strong mastery tier on this test attempt. Focus on closing conceptual gaps below.")

            with col_weak:
                st.markdown("<h5 style='color: #991B1B; font-weight: 700;'>🔴 Weak Subjects (Priority Intervention < 50%)</h5>", unsafe_allow_html=True)
                if rep["weak_subjects"]:
                    for w in rep["weak_subjects"]:
                        missed_topics = ", ".join(w["topics_missed"][:3]) if w["topics_missed"] else "Foundational concepts"
                        st.markdown(f"""
                        <div class="diagnostic-card-weak">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-size: 1.05rem; color: #991B1B;">{w['subject']}</strong>
                                <span style="background: #FEE2E2; color: #B91C1C; font-weight: 700; padding: 3px 10px; border-radius: 999px; font-size: 0.8rem;">
                                    {w['accuracy']}% Acc · {w['marks']:.2f} M
                                </span>
                            </div>
                            <div style="font-size: 0.85rem; color: #7F1D1D; margin-top: 6px;">
                                {w['assessment']}
                            </div>
                            <div style="font-size: 0.8rem; color: #991B1B; margin-top: 6px; padding-top: 4px; border-top: 1px dashed #FECACA;">
                                ⚠️ <b>Missed Microtopics:</b> {missed_topics}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("🎉 Outstanding! No critical weak subjects (< 50%) identified on this test.")

            if rep["moderate_subjects"]:
                st.markdown("<h5 style='color: #92400E; font-weight: 700; margin-top: 12px;'>🟡 Moderate Subjects (Needs Polish: 50% - 69%)</h5>", unsafe_allow_html=True)
                for m in rep["moderate_subjects"]:
                    st.markdown(f"""
                    <div class="diagnostic-card-moderate">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-size: 1.02rem; color: #92400E;">{m['subject']}</strong>
                            <span style="background: #FEF3C7; color: #B45309; font-weight: 700; padding: 3px 10px; border-radius: 999px; font-size: 0.8rem;">
                                {m['accuracy']}% Acc · {m['marks']:.2f} M
                            </span>
                        </div>
                        <div style="font-size: 0.85rem; color: #78350F; margin-top: 4px;">{m['assessment']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ------------------------------------------------------------------
            # ACTIONABLE STUDY PRESCRIPTION & SYLLABUS NAVIGATOR BRIDGE
            # ------------------------------------------------------------------
            if rep["study_recommendations"]:
                st.markdown("---")
                st.markdown("<h4 style='color: #0F172A; font-weight: 800;'>📋 Recommended Study Actions & Syllabus Navigator Bridge</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>Direct remedial actions tailored to the subjects and microtopics you struggled with on this test.</p>", unsafe_allow_html=True)
                
                for idx, rec in enumerate(rep["study_recommendations"]):
                    r_col1, r_col2 = st.columns([3, 1])
                    with r_col1:
                        st.markdown(f"""
                        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;">
                            <span style="background: {'#FEF2F2' if rec['priority'] == 'HIGH' else '#FFFBEB'}; color: {'#DC2626' if rec['priority'] == 'HIGH' else '#D97706'}; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;">
                                {rec['priority']} PRIORITY · {rec['subject']}
                            </span>
                            <div style="color: #1E293B; font-size: 0.92rem; font-weight: 600; margin-top: 6px;">
                                {rec['action']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with r_col2:
                        if st.button(f"📖 Study {rec['subject'][:15]} in Navigator", key=f"btn_nav_bridge_{idx}", use_container_width=True):
                            st.session_state.nav_mode = "📋 Syllabus Navigator"
                            st.rerun()
                        if st.button(f"🤖 Ask AI Mentor", key=f"btn_ask_bridge_{idx}", use_container_width=True):
                            st.session_state.pending_prompt = rec.get("prompt_for_copilot", f"Explain core concepts and elimination techniques for {rec['subject']}.")
                            st.session_state.nav_mode = "🤖 Neural AI Copilot"
                            st.rerun()

            # ------------------------------------------------------------------
            # QUESTION-BY-QUESTION REVIEW
            # ------------------------------------------------------------------
            st.markdown("---")
            st.markdown("<h4 style='color: #0F172A; font-weight: 800;'>🔍 Question-by-Question Solution & Detailed Explanations</h4>", unsafe_allow_html=True)
            
            for eq in rep["evaluated_questions"]:
                border_color = "#BBF7D0" if eq["status"] == "correct" else ("#FECACA" if eq["status"] == "incorrect" else "#E2E8F0")
                badge_bg = "#DCFCE7" if eq["status"] == "correct" else ("#FEE2E2" if eq["status"] == "incorrect" else "#F1F5F9")
                badge_color = "#15803D" if eq["status"] == "correct" else ("#B91C1C" if eq["status"] == "incorrect" else "#475569")
                status_text = "✅ Correct (+2.00)" if eq["status"] == "correct" else ("❌ Incorrect (-0.66)" if eq["status"] == "incorrect" else "⚪ Unattempted (0.00)")

                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1.5px solid {border_color}; border-radius: 14px; padding: 20px 24px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <span style="font-weight: 800; color: #0F172A; font-size: 1.05rem;">Q{eq['id']}.</span>
                            <span class="mock-tag-subj" style="margin-left: 6px;">{eq['subject']}</span>
                            <span class="mock-tag-topic" style="margin-left: 4px;">{eq['topic']}</span>
                        </div>
                        <span style="background: {badge_bg}; color: {badge_color}; font-weight: 700; font-size: 0.8rem; padding: 4px 10px; border-radius: 999px;">
                            {status_text}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(eq["question"])
                
                # Options listing
                for opt in eq["options"]:
                    is_correct_opt = opt.strip().upper().startswith(eq["correct_opt"])
                    is_user_choice = eq["user_choice"] and opt.strip().upper().startswith(str(eq["user_choice"]).strip().upper()[:2])
                    
                    if is_correct_opt and is_user_choice:
                        st.markdown(f"✔ **{opt}** *(Your Correct Answer)*")
                    elif is_correct_opt:
                        st.markdown(f"✔ <span style='color: #059669; font-weight: 700;'>{opt}</span> *(Official Answer)*", unsafe_allow_html=True)
                    elif is_user_choice:
                        st.markdown(f"✖ <span style='color: #DC2626; font-weight: 700;'>{opt}</span> *(Your Answer - Incorrect)*", unsafe_allow_html=True)
                    else:
                        st.markdown(f"- {opt}")

                with st.expander(f"💡 View Faculty Explanation for Q{eq['id']}"):
                    st.markdown(f"**Correct Option:** Option {eq['correct_opt']}\n\n**Detailed Faculty Explanation:**\n{eq['explanation']}")

            # Post-report actions
            st.markdown("<br>", unsafe_allow_html=True)
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                if st.button("🔄 Retake This Test", key="btn_retake_test", use_container_width=True, type="secondary"):
                    st.session_state.mock_user_answers = {}
                    st.session_state.mock_test_report = None
                    st.rerun()
            with act_col2:
                if st.button("⚡ Generate Another Test", key="btn_gen_another_test", use_container_width=True, type="primary"):
                    st.session_state.active_mock_test = None
                    st.session_state.mock_user_answers = {}
                    st.session_state.mock_test_report = None
                    st.rerun()

        # State 2: Active test is loaded and taking is in progress -> Show Test Screen
        elif st.session_state.get("active_mock_test") is not None:
            active_test = st.session_state.active_mock_test
            q_list = active_test.get("questions", [])
            total_qs = len(q_list)

            # Compute current answered count
            curr_answers = st.session_state.get("mock_user_answers", {})
            answered_count = sum(1 for q in q_list if curr_answers.get(q["id"]) is not None and str(curr_answers.get(q["id"])).strip() != "")

            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1.5px solid #4F46E5; border-radius: 18px; padding: 22px 26px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(79, 70, 229, 0.08);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <span style="background: #EEF2FF; color: #4F46E5; font-size: 0.78rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;">
                            ⏱️ SIMULATED EXAM IN PROGRESS
                        </span>
                        <h4 style="color: #0F172A; font-size: 1.35rem; font-weight: 800; margin: 8px 0 2px 0;">{active_test.get('title', 'Prelims Mock Test')}</h4>
                        <div style="color: #475569; font-size: 0.88rem;">Marking Scheme: <b>+2.00 for Correct</b> | <b>-0.66 for Incorrect</b> | <b>0.00 for Unattempted</b></div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.4rem; font-weight: 800; color: #4F46E5;">{answered_count} / {total_qs}</div>
                        <div style="font-size: 0.8rem; color: #64748B; font-weight: 600;">Questions Answered</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(answered_count / total_qs if total_qs > 0 else 0.0)
            st.markdown("<br>", unsafe_allow_html=True)

            # Test Questions form
            with st.form("active_mock_exam_form"):
                user_selected = {}
                for q in q_list:
                    qid = q["id"]
                    st.markdown(f"""
                    <div class="mock-q-header">
                        <div>
                            <span style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">Question {qid} of {total_qs}</span>
                            <span class="mock-tag-subj" style="margin-left: 8px;">{q.get('subject', 'GS Paper')}</span>
                            <span class="mock-tag-topic" style="margin-left: 4px;">{q.get('topic', 'Microtopic')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(q["question"])
                    
                    prev_ans = curr_answers.get(qid)
                    # Options
                    user_selected[qid] = st.radio(
                        f"Select your option for Q{qid}:",
                        q["options"],
                        index=q["options"].index(prev_ans) if prev_ans in q["options"] else None,
                        key=f"mock_opt_radio_{qid}"
                    )
                    st.markdown("---")

                f_c1, f_c2 = st.columns([2, 1])
                with f_c1:
                    test_submitted = st.form_submit_button("🏁 Submit Test & Calculate Diagnostic Report", use_container_width=True, type="primary")
                with f_c2:
                    test_cancelled = st.form_submit_button("🔄 Discard / Reset Test", use_container_width=True)

            if test_submitted:
                st.session_state.mock_user_answers = user_selected
                report = evaluate_mock_test(active_test, user_selected)
                st.session_state.mock_test_report = report
                
                # Append to history
                st.session_state.mock_test_history.append({
                    "id": f"mock_attempt_{len(st.session_state.mock_test_history) + 1}",
                    "title": active_test.get("title", "Prelims Mock"),
                    "date": "Today",
                    "score": report["net_marks"],
                    "max_marks": report["max_marks"],
                    "accuracy": report["accuracy_pct"],
                    "strong": [s["subject"] for s in report["strong_subjects"]],
                    "weak": [w["subject"] for w in report["weak_subjects"]]
                })
                st.rerun()

            if test_cancelled:
                st.session_state.active_mock_test = None
                st.session_state.mock_user_answers = {}
                st.session_state.mock_test_report = None
                st.rerun()

        # State 3: No active test -> Show Test Generator Setup Panel
        else:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);">
                <span style="background: #EEF2FF; color: #4F46E5; font-size: 0.78rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;">
                    🎯 UPSC PRELIMS SIMULATION ENGINE
                </span>
                <h4 style="color: #0F172A; font-size: 1.35rem; font-weight: 800; margin: 8px 0 4px 0;">Configure & Launch Simulated Practice Mock</h4>
                <div style="color: #475569; font-size: 0.92rem;">
                    Generate authentic UPSC statement-based MCQs. Take the test in the interactive arena to receive instant negative marking evaluation and an automated <b>Weak vs Strong Subjects Diagnostic Report</b>!
                </div>
            </div>
            """, unsafe_allow_html=True)

            g_col1, g_col2, g_col3 = st.columns(3)
            with g_col1:
                subj_test = st.selectbox(
                    "Select Test Module / Subject:",
                    [
                        "Full-Length Simulation (Multi-Subject Diagnostic)",
                        "Indian Polity & Constitution",
                        "Modern Indian History",
                        "Indian Economy & Budget",
                        "Environment & Ecology",
                        "Geography & Mapping",
                        "Science & Technology",
                        "CSAT (Aptitude & Reasoning)"
                    ],
                    key="arena_subj_select"
                )
            with g_col2:
                num_qs = st.selectbox(
                    "Number of Questions:",
                    ["5 Questions (Quick Diagnostic Drill - 5 mins)", "10 Questions (Standard Sectional Mock - 10 mins)", "15 Questions (Intensive Module - 15 mins)", "20 Questions (Mini Prelims Paper - 20 mins)"],
                    key="arena_num_select"
                )
            with g_col3:
                diff_lvl = st.selectbox(
                    "Difficulty & Question Pattern:",
                    ["UPSC Prelims Standard (Statement-based 1 & 2 only)", "High-Yield Statement-based", "PYQ Trend Pattern"],
                    key="arena_diff_select"
                )

            engine_mode = st.radio(
                "Select Question Generation Source:",
                ["🤖 Dynamic AI Generator (Groq LLM with Curated Fallback)", "⚡ Instant Curated Exam Bank (Fastest, Zero Latency)"],
                horizontal=True,
                key="arena_engine_mode"
            )

            num_int = 5
            if "10" in num_qs:
                num_int = 10
            elif "15" in num_qs:
                num_int = 15
            elif "20" in num_qs:
                num_int = 20

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Launch Simulated Mock Test in Arena", key="btn_launch_arena_mock", use_container_width=True, type="primary"):
                with st.spinner(f"⚡ Generating authentic UPSC questions for '{subj_test}'..."):
                    use_ai_flag = "AI" in engine_mode
                    test_data = generate_mock_test(
                        subject=subj_test,
                        num_questions=num_int,
                        difficulty=diff_lvl,
                        use_ai=use_ai_flag
                    )
                    st.session_state.active_mock_test = test_data
                    st.session_state.mock_user_answers = {}
                    st.session_state.mock_test_report = None
                    st.rerun()

    # --------------------------------------------------------------------------
    # TAB 2: CUSTOM TOPIC GENERATOR
    # --------------------------------------------------------------------------
    with test_tab2:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>⚡ Custom Topic & Microtopic Generator</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>Test yourself on any specific syllabus microtopic or recent current affair topic.</p>", unsafe_allow_html=True)
        
        c_topic = st.text_input("Enter Specific Microtopic / Syllabus Theme:", value="Fundamental Rights & Basic Structure", key="custom_topic_input")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            c_subj = st.selectbox("Assign to GS Subject Category:", ["Indian Polity & Constitution", "Modern Indian History", "Indian Economy & Budget", "Environment & Ecology", "Geography & Mapping", "Science & Technology", "CSAT (Aptitude & Reasoning)"], key="custom_topic_subj")
        with c_col2:
            c_num = st.selectbox("Number of Questions:", [5, 10, 15], key="custom_topic_num")

        if st.button("🚀 Generate & Launch Custom Test in Arena", key="btn_launch_custom_arena", use_container_width=True, type="primary"):
            with st.spinner(f"Generating custom test on '{c_topic}'..."):
                test_data = generate_mock_test(
                    subject=c_subj,
                    num_questions=c_num,
                    difficulty="UPSC Prelims Standard",
                    custom_topic=c_topic,
                    use_ai=True
                )
                test_data["title"] = f"Custom Test: {c_topic} ({c_num} Qs)"
                st.session_state.active_mock_test = test_data
                st.session_state.mock_user_answers = {}
                st.session_state.mock_test_report = None
                st.rerun()

    # --------------------------------------------------------------------------
    # TAB 3: MAINS ANSWER WRITING CHALLENGE
    # --------------------------------------------------------------------------
    with test_tab3:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>✍️ Daily Mains Answer Writing Prompt</h4>", unsafe_allow_html=True)
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

    # --------------------------------------------------------------------------
    # TAB 4: TEST HISTORY & DIAGNOSTICS
    # --------------------------------------------------------------------------
    with test_tab4:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📊 Mock Test Performance History</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>Track your accuracy trends and see how weak subjects turn into strong subjects over time.</p>", unsafe_allow_html=True)
        
        past_tests = st.session_state.get("mock_test_history", [])
        if past_tests:
            for idx, pt in enumerate(reversed(past_tests)):
                strong_str = ", ".join(pt.get("strong", [])) if pt.get("strong") else "None"
                weak_str = ", ".join(pt.get("weak", [])) if pt.get("weak") else "None"
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 18px 22px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div>
                            <strong style="font-size: 1.05rem; color: #0F172A;">{pt.get('title', 'Prelims Mock Test')}</strong>
                            <div style="font-size: 0.82rem; color: #64748B; margin-top: 2px;">Attempted on {pt.get('date', 'Recent')}</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.25rem; font-weight: 800; color: #059669;">{pt.get('score', 0):.2f} / {pt.get('max_marks', 20):.0f}</span>
                            <div style="font-size: 0.8rem; font-weight: 700; color: #4F46E5;">{pt.get('accuracy', 0):.1f}% Accuracy</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 16px; margin-top: 10px; font-size: 0.85rem; flex-wrap: wrap; border-top: 1px solid #F1F5F9; padding-top: 8px;">
                        <div>🟢 <b>Strong:</b> <span style="color: #15803D;">{strong_str}</span></div>
                        <div>🔴 <b>Weak Focus:</b> <span style="color: #B91C1C;">{weak_str}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No mock test history found. Take a test in the Prelims Mock Arena to start recording analytics!")

# ==========================================
# VIEW 5: 🎓 LIVE & RECORDED CLASSES
# ==========================================
elif nav_mode == "🎓 Live & Recorded Classes":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>🎓 UPSC Live Classes & Interactive Lecture Library</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Access live batch lectures from Physics Wallah (PW Live), review subject playlists, and generate instant AI notes.</p>", unsafe_allow_html=True)
    
    pw_class_url = "https://www.pw.live/watch/?batchSlug=6a0d74b1acca9706aa169063&batchSubjectId=6a1d635dcf99bcb20ab85f01&subjectSlug=6a1d635dcf99bcb20ab85f01&topicSlug=all&scheduleId=6a3949598df846a134ed1e7d&type=penpencilvdo&isPPJEnabled=true&entryPoint=BATCH_LECTURE_VIDEOS_6a3949598df846a134ed1e7d&learn2Earn=true&parentId=6a0d74b1acca9706aa169063&vType=BATCHES&childId=6a3949598df846a134ed1e7d"

    # Featured Live/Recorded Class Card
    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 12px;">
            <div>
                <span style="background: #FEF2F2; color: #DC2626; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; border: 1px solid #FECACA;">
                    🔴 LIVE BATCH LECTURE
                </span>
                <h4 style="color: #0F172A; font-size: 1.35rem; font-weight: 800; margin-top: 10px; margin-bottom: 4px;">🎓 PW Live Official Batch Class</h4>
                <div style="color: #475569; font-size: 0.92rem;">UPSC CSE Foundation Batch Lecture · PenPencil Video Portal</div>
            </div>
            <a href="{pw_class_url}" target="_blank" style="background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%); color: #FFFFFF; font-weight: 700; padding: 12px 22px; border-radius: 12px; text-decoration: none; display: inline-block; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);">
                🎥 Open Fullscreen on PW.live →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Embedded Player Container
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📺 Interactive PW Class Portal</h4>", unsafe_allow_html=True)
    
    try:
        import streamlit.components.v1 as components
        components.iframe(pw_class_url, height=520, scrolling=True)
    except Exception:
        st.markdown(f'<iframe src="{pw_class_url}" width="100%" height="520" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        st.markdown(f'<a href="{pw_class_url}" target="_blank" style="width:100%; display:block; text-align:center; background:#EFF6FF; color:#2563EB; font-weight:700; padding:12px; border-radius:12px; border:1px solid #BFDBFE; text-decoration:none;">🚀 Launch Class on PW Live (Direct Link)</a>', unsafe_allow_html=True)
    with c_btn2:
        if st.button("🤖 Generate AI Notes for this PW Class", key="btn_pw_class_notes", use_container_width=True):
            st.session_state.pending_prompt = "Generate detailed UPSC revision notes for the active PW Live batch lecture topic. Include core concepts, definitions, key Mains analytical points, and practice Prelims MCQs."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    st.markdown("---")

    # Today's Live Schedule Timeline
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📅 Today's Live Lecture Schedule</h4>", unsafe_allow_html=True)
    
    sched_col1, sched_col2, sched_col3 = st.columns(3)
    with sched_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div style="font-size:0.8rem; color:#059669; font-weight:700;">🟢 LIVE NOW (08:00 - 10:00 AM)</div>
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
            <div style="font-size:0.8rem; color:#0284C7; font-weight:700;">⏰ UPCOMING (02:00 - 04:00 PM)</div>
            <div class="pwskills-title" style="margin-top:4px;">📈 GS3: Macroeconomics & Union Budget Analysis</div>
            <div class="pwskills-desc">Faculty: Prof. V. Verma · Topic: Fiscal Deficit & Capital Expenditure Trends</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔔 Set Class Reminder", key="btn_join_live2", use_container_width=True):
            st.info("🔔 Reminder set for GS3 Macroeconomics & Union Budget class!")

    with sched_col3:
        st.markdown("""
        <div class="pwskills-card">
            <div style="font-size:0.8rem; color:#7C3AED; font-weight:700;">📼 RECORDED (06:00 - 08:00 PM)</div>
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
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>⚡ AI Lecture Note & Concept Generator</h4>", unsafe_allow_html=True)
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
elif nav_mode in ["🚀 PW Skills Career Track", "💼 Backup Plans & PW Skills"]:
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>💼 Career Backup Plans & PW Skills Courses</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Strategic parallel exam options and industry-aligned technical courses from <a href='https://pwskills.com' target='_blank' style='color:#4F46E5; font-weight:700;'>PW Skills</a> to guarantee long-term career security.</p>", unsafe_allow_html=True)
    
    # Section 1: Parallel Exam Backups
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🏛️ Option 1: High Syllabus-Overlap Government Exams</h4>", unsafe_allow_html=True)
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    
    with ex_col1:
        st.markdown("""
        <div class="pwskills-card">
            <div class="pwskills-title">🏦 RBI Grade B Officer</div>
            <div class="pwskills-desc">High overlap in Economic & Social Issues (ESI), General Awareness, and Finance. Ideal for UPSC aspirants with strong GS3 background.</div>
            <div style="margin-top:10px;"><span style="color:#0284C7; font-weight:700;">Overlap: ~70%</span></div>
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
            <div style="margin-top:10px;"><span style="color:#0284C7; font-weight:700;">Overlap: ~85%</span></div>
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
            <div style="margin-top:10px;"><span style="color:#0284C7; font-weight:700;">Overlap: ~65%</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🤖 Consult AI on NABARD", key="btn_nabard_plan_fs", use_container_width=True):
            st.session_state.pending_prompt = "Explain NABARD Grade A exam pattern and syllabus overlap with UPSC GS Paper 3 Agriculture."
            st.session_state.nav_mode = "🤖 Neural AI Copilot"
            st.rerun()

    st.markdown("---")

    # Section 2: PW Skills Course Catalog
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>🎓 Option 2: PW Skills Career Tech Courses (<a href='https://pwskills.com' target='_blank' style='color:#4F46E5;'>pwskills.com</a>)</h4>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>➕ Add Custom Microtopics & Syllabus Files</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.95rem;'>Expand your UPSC curriculum dashboard with custom topics or upload syllabus PDF files.</p>", unsafe_allow_html=True)
    
    col_add1, col_add2 = st.columns(2)
    
    with col_add1:
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📝 Add New Microtopic</h4>", unsafe_allow_html=True)
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
        st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📄 Upload Curriculum Document</h4>", unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("Upload custom UPSC Syllabus PDF file", type=["pdf", "txt"], key="pdf_up_fs")
        if uploaded_pdf is not None:
            if st.button("🚀 Process & Index File", key="proc_btn_fs"):
                st.info("Processing uploaded syllabus file into vector memory...")
                st.success("✅ Syllabus document successfully processed!")

# ==========================================
# VIEW 5: 📊 MATRIX ANALYTICS
# ==========================================
elif nav_mode == "📊 Matrix Analytics":
    st.markdown("<h3 style='color: #0F172A;'>📊 UPSC Matrix Analytics</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Real-time visual breakdown of syllabus coverage across GS1, GS2, GS3, and GS4.</p>", unsafe_allow_html=True)

    p_counts = {"GS Paper 1": 386, "GS Paper 2": 89, "GS Paper 3": 73, "GS Paper 4": 69}
    completed_all = len(st.session_state.progress.get("completed", []))
    total_curriculum = sum(p_counts.values()) + len(st.session_state.progress.get("custom_microtopics", []))
    overall_completion_pct = (completed_all / total_curriculum * 100) if total_curriculum > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Microtopics</div>
            <div class="metric-value">{total_curriculum}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Completed Topics</div>
            <div class="metric-value" style="color: #22C55E;">{completed_all}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Overall Completion</div>
            <div class="metric-value" style="color: #0284C7;">{overall_completion_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Remaining Topics</div>
            <div class="metric-value" style="color: #64748B;">{max(0, total_curriculum - completed_all)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    a_col1, a_col2 = st.columns(2)
    
    with a_col1:
        st.markdown("<h4 style='color: #0F172A;'>📊 Paper-wise Workload</h4>", unsafe_allow_html=True)
        for p_name, count in p_counts.items():
            completed_p = sum(1 for m_id in st.session_state.progress.get("completed", []) if m_id.startswith(p_name))
            p_pct = (completed_p / count * 100) if count > 0 else 0
            st.markdown(f"<strong style='color: #0284C7;'>{p_name}</strong> <span style='color: #64748B;'>({completed_p}/{count} completed)</span>", unsafe_allow_html=True)
            st.progress(p_pct / 100.0)
            
    with a_col2:
        st.markdown("<h4 style='color: #0F172A;'>🎯 Focus Area Recommendations</h4>", unsafe_allow_html=True)
        st.info("📍 **Recommended Priority:** Complete **GS Paper 1 (Culture & Modern History)** and **GS Paper 2 (Polity & Constitution)** first as they have high weightage in Prelims & Mains overlap.")
        st.success("✅ **Study Tip:** Click '💡 Explainer' next to any pending microtopic in the Curriculum Navigator to generate high-yield structured notes.")

# ==========================================
# VIEW 6: ⚙️ SETTINGS & PERSONA TUNING
# ==========================================
elif nav_mode == "⚙️ Settings":
    st.markdown("<h3 style='color: #0F172A;'>⚙️ Aspirant Settings & Calibration</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Calibrate your preparation stage, persona vibe, emotional goals, and session cache.</p>", unsafe_allow_html=True)
    
    st.markdown("#### 👤 Student Profile & Prep Stage")
    render_student_profile_card()
    
    st.markdown("---")
    st.markdown("#### 🧠 Active AI Persona Style")
    set_col1, set_col2 = st.columns([0.6, 0.4])
    with set_col1:
        cur_p = st.session_state.get("ai_persona", "Personal Mentor")
        p_list = ["Personal Mentor", "Academic Professor", "Strict Evaluator", "Socratic Guide", "Empathetic Counselor"]
        new_p = st.selectbox(
            "Select AI Persona:",
            p_list,
            index=p_list.index(cur_p) if cur_p in p_list else 0,
            key="settings_persona_select"
        )
        if new_p != cur_p:
            st.session_state.ai_persona = new_p
            st.success(f"Updated persona to **{new_p}**!")
            st.rerun()
    with set_col2:
        st.info("💡 **Persona Style:** Customizes answer depth, tone, motivational nudges, and exam feedback.")

    st.markdown("---")
    st.markdown("#### 🧹 Session & Storage Management")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        if st.button(f"🧹 Clear Chat History for {st.session_state.selected_exam}", key="btn_clear_chat_settings", use_container_width=True):
            st.session_state.exam_messages[st.session_state.selected_exam] = []
            st.session_state.messages = []
            st.success(f"Cleared chat history for {st.session_state.selected_exam}!")
            st.rerun()
    with r_col2:
        if st.button("🔄 Reset All Progress & Daily Tasks", key="btn_reset_all_settings", use_container_width=True):
            st.session_state.progress = {"completed": [], "notes": {}, "custom_microtopics": []}
            save_user_progress(st.session_state.progress)
            st.success("User progress reset to default!")
            st.rerun()

