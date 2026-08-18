from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import LLM_FALLBACK_MODELS, LLM_MODEL, get_groq_client
from generation.prompts import (
    ACADEMIC_LLM_FALLBACK_TEMPLATE,
    ACADEMIC_SYSTEM_PROMPT,
    ACADEMIC_USER_TEMPLATE,
    ACADEMIC_WEB_ONLY_TEMPLATE,
    GENERAL_FALLBACK,
    MENTAL_HEALTH_SYLLABUS_SYSTEM_PROMPT,
    NON_ACADEMIC_SYSTEM_PROMPT,
    RELATIONSHIP_SYLLABUS_SYSTEM_PROMPT,
)
from ingestion.indexer import VectorIndex, load_index
from retrieval.intent_router import (
    IntentResult,
    classify_intent,
    get_clarification_message,
)
from retrieval.relevance import is_kb_relevant
from retrieval.web_search import format_web_context, search_upsc_topic


def extract_topic_name(query: str) -> str:
    quote_match = re.search(r"['\"]([^'\"]{3,100})['\"]", query)
    if quote_match:
        return quote_match.group(1).strip()
    clean = re.sub(
        r"(?i)^(Overview for|explain|notes on|what is|describe|provide|give|generate|details on)\s+(the\s+)?(upsc\s+)?(mains\s+)?(microtopic\s+)?",
        "",
        query,
    ).strip()
    clean = re.sub(r"(?i)\s+under\s+.*$", "", clean).strip()
    clean = re.sub(r"(?i)\s+in\s+detail.*$", "", clean).strip()
    clean = re.sub(r"(?i)\s+include\s+.*$", "", clean).strip()
    return clean.capitalize() if clean else query


def generate_academic_fallback(query: str) -> str:
    title = extract_topic_name(query)
    return (
        f"### 📖 Expert Faculty Explanation & Core Analysis\n\n"
        f"**Executive Summary (Prelims-Ready Definition):**\n"
        f"**{title}** is a pivotal subject area within the UPSC Civil Services Examination framework (covering General Studies Papers 1, 2, 3 & 4), demanding a structured understanding of foundational concepts, historical evolution, statutory provisions, and modern policy implications.\n\n"
        f"---\n\n"
        f"#### 🔍 Key Conceptual Dimensions & Detailed Breakdown:\n"
        f"1. **Core Conceptual & Theoretical Foundation:**\n"
        f"   - **Background & Context:** {title} represents a fundamental component of India's governance, administrative history, and constitutional evolution.\n"
        f"   - **Institutional Framework:** Encompasses key statutory bodies, judicial interpretations, legislative mandates, and executive policies.\n\n"
        f"2. **Socio-Economic & Administrative Significance:**\n"
        f"   - **Governance Impact:** Drives public service delivery, constitutional accountability, institutional transparency, and administrative efficiency.\n"
        f"   - **Stakeholder Dynamics:** Affects citizen rights, socio-economic equity, structural reforms, and sustainable growth objectives.\n\n"
        f"3. **Contemporary Challenges & Policy Bottlenecks:**\n"
        f"   - **Implementation Challenges:** Capacity constraints, inter-departmental coordination gaps, and resource allocation issues.\n"
        f"   - **Reform Roadmap:** Emphasizes technology integration, administrative decentralization, and evidence-based policy formulation.\n\n"
        f"---\n\n"
        f"### 📊 Exam Angle (Prelims & Mains Focus)\n\n"
        f"🎯 **UPSC Prelims Strategic Focus:**\n"
        f"- Pay specific attention to chronological timelines, specific constitutional articles/statutes, nodal ministries, and committee recommendations related to **{title}**.\n"
        f"- Watch out for common Prelims trap options regarding executive discretion vs statutory mandates.\n\n"
        f"🎯 **UPSC Mains Strategic Focus (GS Answer Writing):**\n"
        f"- **Introduction:** Start with a 2-line contextual definition or recent landmark event/statute related to **{title}**.\n"
        f"- **Body:** Structure using multi-dimensional subheadings (Administrative, Economic, Social, Legal) backed by Law Commission / NITI Aayog / Supreme Court precedents.\n"
        f"- **Conclusion:** End with a forward-looking, constructive 'Way Forward' emphasizing constitutional vision.\n\n"
        f"---\n\n"
        f"### 📝 Practice MCQs & UPSC Prelims Questions\n\n"
        f"**Question 1:** With reference to **{title}**, consider the following statements:\n"
        f"1. It forms an integral component of the operational framework of Indian governance.\n"
        f"2. Comprehensive analysis requires evaluating core statutory principles alongside contemporary policy initiatives.\n\n"
        f"Which of the statements given above is/are correct?\n"
        f"- **A)** 1 only\n"
        f"- **B)** 2 only\n"
        f"- **C)** Both 1 and 2\n"
        f"- **D)** Neither 1 nor 2\n\n"
        f"**Correct Answer:** Option **C**\n"
        f"**Explanation:** Both statements are correct. UPSC Civil Services examination requires synthesizing theoretical foundations with contemporary policy developments regarding {title}.\n\n"
        f"**Question 2:** Which of the following best reflects the primary objective of institutional reforms surrounding **{title}**?\n"
        f"- **A)** Restricting administrative oversight and statutory compliance\n"
        f"- **B)** Enhancing institutional transparency, public welfare, and operational efficiency\n"
        f"- **C)** Promoting rigid centralized decision-making frameworks\n"
        f"- **D)** Excluding non-governmental stakeholders from policy processes\n\n"
        f"**Correct Answer:** Option **B**\n"
        f"**Explanation:** Effective administrative governance models focus on public welfare, transparency, institutional efficiency, and citizen-centric service delivery.\n\n"
        f"---\n\n"
        f"### ✍️ UPSC Mains Practice Questions\n\n"
        f"**Mains Question 1 (10 Marks / 150 Words):**\n"
        f"\"Critically analyze the significance of **{title}** in modern Indian governance. What structural measures are required to strengthen its effective implementation?\"\n\n"
        f"- **Answer Writing Approach:**\n"
        f"  - **Introduction (20-30 words):** Define {title} in the context of GS Mains syllabus.\n"
        f"  - **Core Body Points (90-100 words):**\n"
        f"    - Highlight key administrative and constitutional benefits.\n"
        f"    - Discuss existing institutional bottlenecks (capacity, funding, coordination).\n"
        f"  - **Conclusion (20-30 words):** Conclude with actionable recommendations and NITI Aayog / Committee references.\n\n"
        f"**Mains Question 2 (15 Marks / 250 Words):**\n"
        f"\"Examine the multi-dimensional challenges associated with **{title}**. How can policy intervention and digital governance tools resolve these bottlenecks? Discuss.\"\n\n"
        f"- **Answer Writing Approach:**\n"
        f"  - **Introduction (30-40 words):** Provide contextual background and current relevance of {title}.\n"
        f"  - **Core Body Points (160-180 words):**\n"
        f"    - Multi-dimensional breakdown: Legal & Statutory, Socio-Economic, Administrative.\n"
        f"    - Role of technology (e-governance, AI, data analytics) in overcoming bottlenecks.\n"
        f"  - **Conclusion / Way Forward (30-40 words):** Forward-looking roadmap aligned with constitutional ideals."
    )


class RAGChatbot:
    def __init__(self, index: Optional[VectorIndex] = None):
        self.index = index or load_index()
        self.client = get_groq_client()
        self.pyq_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "modern_history_pyqs.json"
        )
        self.pyqs = []
        if self.pyq_path.exists():
            with open(self.pyq_path, encoding="utf-8") as f:
                self.pyqs = json.load(f)

    def generate_academic_fallback(self, query: str) -> str:
        return generate_academic_fallback(query)

    def _generate_academic_fallback(self, query: str) -> str:
        return generate_academic_fallback(query)

    def _extract_topic_name(self, query: str) -> str:
        return extract_topic_name(query)

    def _ensure_prelims_questions(self, answer: str, query: str) -> str:
        if "Practice MCQs" in answer or "Question 1:" in answer or "📝" in answer:
            return answer

        title = extract_topic_name(query)
        prelims_block = (
            f"\n\n### 📝 Practice MCQs & UPSC Prelims Questions\n\n"
            f"**Question 1:** With reference to **{title}**, consider the following statements:\n"
            f"1. It forms an integral component of the operational framework of Indian governance.\n"
            f"2. Comprehensive analysis requires evaluating core statutory principles alongside contemporary policy initiatives.\n\n"
            f"Which of the statements given above is/are correct?\n"
            f"- **A)** 1 only\n"
            f"- **B)** 2 only\n"
            f"- **C)** Both 1 and 2\n"
            f"- **D)** Neither 1 nor 2\n\n"
            f"**Correct Answer:** Option **C**\n"
            f"**Explanation:** Both statements are correct. UPSC Civil Services examination requires evaluating core concepts alongside contemporary policy developments.\n\n"
            f"**Question 2:** Which of the following best reflects the primary objective of studying **{title}** for UPSC?\n"
            f"- **A)** Isolated rote learning\n"
            f"- **B)** Developing multi-dimensional conceptual clarity for GS answer writing\n"
            f"- **C)** Technical specialization in non-syllabus areas\n"
            f"- **D)** None of the above\n\n"
            f"**Correct Answer:** Option **B**\n"
            f"**Explanation:** UPSC evaluates candidates on analytical synthesis, policy awareness, and structured answer writing."
        )
        return answer.strip() + prelims_block

    def _ensure_mains_questions(self, answer: str, query: str) -> str:
        if (
            "Mains Practice Questions" in answer
            or "Mains Question" in answer
            or "✍️" in answer
        ):
            return answer

        title = extract_topic_name(query)
        mains_block = (
            f"\n\n### ✍️ UPSC Mains Practice Questions\n\n"
            f"**Mains Question 1 (10 Marks / 150 Words):**\n"
            f"\"Critically analyze the core dimensions and significance of **{title}** in contemporary Indian governance.\"\n\n"
            f"- **Answer Writing Approach:**\n"
            f"  - **Introduction:** Briefly define {title} and contextualize its syllabus relevance (2 lines).\n"
            f"  - **Core Body Points:** Highlight key structural aspects, constitutional/statutory links, and challenges.\n"
            f"  - **Conclusion / Way Forward:** Provide a balanced, forward-looking concluding observation.\n\n"
            f"**Mains Question 2 (15 Marks / 250 Words):**\n"
            f"\"Discuss the major challenges associated with **{title}**. What policy and institutional reforms are needed to address these effectively?\"\n\n"
            f"- **Answer Writing Approach:**\n"
            f"  - **Introduction:** Contextual background of {title}.\n"
            f"  - **Core Body Points:** Multi-dimensional analysis (Administrative, Legal, Socio-Economic) + Committee references.\n"
            f"  - **Conclusion / Way Forward:** Actionable policy recommendations for sustainable outcomes."
        )
        return answer.strip() + mains_block

    def _llm_complete(
        self, user_message: str, system_prompt: str = ACADEMIC_SYSTEM_PROMPT
    ) -> str:
        models_to_try = [LLM_MODEL] + [
            m for m in LLM_FALLBACK_MODELS if m != LLM_MODEL
        ]
        seen = set()
        unique_models = []
        for m in models_to_try:
            if m not in seen:
                seen.add(m)
                unique_models.append(m)

        last_exception = None
        for model_name in unique_models:
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                )
                content = response.choices[0].message.content or ""
                content = re.sub(
                    r"^<think>.*?</think>\s*", "", content, flags=re.DOTALL
                )
                if content.strip():
                    return content
            except Exception as e:
                print(f"LLM call failed with model {model_name}: {e}")
                last_exception = e
        if last_exception:
            raise last_exception
        return ""

    def _find_relevant_pyqs(self, query: str, top_k: int = 1) -> list[dict]:
        if not self.pyqs:
            return []

        texts = []
        for pyq in self.pyqs:
            texts.append(
                f"{pyq.get('question', '')} {pyq.get('explanation', '')}"
            )

        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform(texts)
            query_vec = vectorizer.transform([query])
            scores = cosine_similarity(query_vec, matrix).flatten()

            ranked = sorted(
                enumerate(scores), key=lambda x: x[1], reverse=True
            )
            results = []
            for idx, score in ranked[:top_k]:
                if score >= 0.15:
                    results.append(self.pyqs[idx])
            return results
        except Exception:
            return []

    def _template_response(self, record: dict) -> dict[str, Any]:
        return {
            "answer": record["answer_template"],
            "intent": record["intent"],
            "category": (
                "non_academic"
                if record.get("category") != "academic"
                else "academic"
            ),
            "confidence": "high",
            "sources": [{"id": record["id"], "question": record["question"]}],
            "mode": "template",
        }

    def _build_kb_context(self, record: Optional[dict]) -> str:
        if not record:
            return "No matching entry in local knowledge base."
        meta = record.get("metadata", {})
        content = record.get("answer_content") or record.get(
            "answer_template", ""
        )
        return (
            f"Topic: {meta.get('syllabus_topic', record.get('question', ''))}\n"
            f"Subject: {meta.get('subject', 'General Studies')}\n"
            f"Content: {content}"
        )

    def _web_results_usable(self, web_results: list[dict]) -> bool:
        if not web_results:
            return False
        if (
            len(web_results) == 1
            and web_results[0].get("title") == "Search unavailable"
        ):
            return False
        return any(r.get("snippet") for r in web_results)

    def _academic_response(
        self,
        query: str,
        rag_record: Optional[dict] = None,
        rag_score: float = 0.0,
        web_results: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        web_results = (
            web_results
            if web_results is not None
            else search_upsc_topic(query)
        )
        web_context = format_web_context(web_results)
        web_ok = self._web_results_usable(web_results)

        use_kb = rag_record and is_kb_relevant(query, rag_record, rag_score)

        if use_kb and web_ok:
            user_msg = ACADEMIC_USER_TEMPLATE.format(
                query=query,
                kb_context=self._build_kb_context(rag_record),
                web_context=web_context,
            )
            mode = "rag+web"
            sources = [
                {
                    "id": rag_record["id"],
                    "question": rag_record["question"],
                    "score": rag_score,
                },
                *[
                    {"title": r["title"], "url": r["url"]}
                    for r in web_results[:3]
                    if r.get("url")
                ],
            ]
            confidence = "high"
        elif web_ok:
            user_msg = ACADEMIC_WEB_ONLY_TEMPLATE.format(
                query=query,
                web_context=web_context,
            )
            mode = "web"
            sources = [
                {"title": r["title"], "url": r["url"]}
                for r in web_results[:3]
                if r.get("url")
            ]
            confidence = "medium"
        else:
            user_msg = ACADEMIC_LLM_FALLBACK_TEMPLATE.format(query=query)
            mode = "llm"
            sources = []
            confidence = "medium"

        try:
            answer = self._llm_complete(
                user_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT
            )
            answer = self._ensure_prelims_questions(answer, query)
            answer = self._ensure_mains_questions(answer, query)
        except Exception as err:
            print(f"LLM completion error in _academic_response: {err}")
            answer = self._generate_academic_fallback(query)
            mode = "fallback"

        pyqs = self._find_relevant_pyqs(query)
        if pyqs:
            pyq_sections = []
            for pyq in pyqs:
                pyq_sections.append(
                    f"\n\n---\n### Sourced from [pwonlyias.com (Modern History Prelims PYQs)](https://pwonlyias.com/prelims-previous-years-paper/modern-history/)\n\n"
                    f"**Related Previous Year Question ({pyq['year']}, Question {pyq['number']}):**\n"
                    f"{pyq['question']}\n\n"
                    f"* **Correct Answer:** {pyq['answer'].upper()}\n"
                    f"* **Explanation:** {pyq['explanation']}"
                )
            answer += "".join(pyq_sections)

        return {
            "answer": answer,
            "intent": "notes_or_explain_topic",
            "category": "academic",
            "confidence": confidence,
            "sources": sources,
            "mode": mode,
        }

    def _handle_academic(
        self, query: str, intent_result: IntentResult
    ) -> dict[str, Any]:
        results = self.index.search(query, top_k=1, category="academic")
        rag_record = results[0]["record"] if results else None
        rag_score = results[0]["score"] if results else 0.0

        result = self._academic_response(query, rag_record, rag_score)
        result["signals"] = intent_result.signals
        return result

    def _postprocess_mental_health_answer(
        self, answer: str, mh_count: int
    ) -> str:
        lines = [
            line
            for line in answer.splitlines()
            if "pwskills" not in line.lower() and "pw skills" not in line.lower()
        ]
        answer = "\n".join(lines)

        helpline_pattern = r"(?s)---\s*\n### 📞 \*\*24/7 Confidential Professional Support Lines.*?(?=---\s*\n🤗|\Z)"

        if mh_count > 0:
            answer = re.sub(helpline_pattern, "", answer)

        if mh_count >= 2:
            card_block = (
                "\n\n---\n\n"
                "🤝 **Professional Psychologist Direct Referral Notice**\n\n"
                "*I recognize that you are navigating persistent emotional distress across multiple queries. While digital psychological coping techniques are helpful for daily stress, ongoing emotional challenges deserve dedicated 1-on-1 consultation with a licensed human psychologist. I am connecting you with professional clinical counseling support below:*\n\n"
                "💳 **Professional Psychologist Contact Card**\n\n"
                "🩺 **Tele MANAS Clinical Psychology Desk (Ministry of Health & Family Welfare)**\n"
                "- **Toll-Free Helpline:** `1-800-891-4416` or `14416` (24/7 Free Tele-Psychology Consultation)\n"
                "- **Official Portal:** [https://telemanas.mohfw.gov.in/](https://telemanas.mohfw.gov.in/)\n\n"
                "👩‍⚕️ **KIRAN Mental Health Rehabilitation Desk**\n"
                "- **Toll-Free Helpline:** `1800-599-0019` (24/7 Multi-lingual Psychological Support)\n\n"
                "🧠 **Vandrevala Clinical Psychological Care**\n"
                "- **Direct Phone:** `+91 9999 666 555`\n"
                "- **Official Portal:** [https://www.vandrevalafoundation.com/](https://www.vandrevalafoundation.com/)\n"
            )
            answer = answer.strip() + card_block

        return answer

    def _generate_mental_health_syllabus_fallback(self, query: str) -> str:
        mood_match = re.search(r"current mental state is '([^']+)'", query, re.I)
        curr_mood = mood_match.group(1) if mood_match else "Mental Health State"

        trigger_match = re.search(r"primary stress trigger is '([^']+)'", query, re.I)
        curr_trigger = trigger_match.group(1) if trigger_match else "Syllabus Anxiety"

        energy_match = re.search(r"daily focus energy level is (\d+/\d+|\d+)", query, re.I)
        energy_str = energy_match.group(1) if energy_match else "5/10"

        comp_match = re.search(r"completed (\d+) microtopics \(([^)]+)\)", query, re.I)
        comp_str = f"{comp_match.group(1)} ({comp_match.group(2)})" if comp_match else "Completed Microtopics"

        rem_match = re.search(r"have (\d+) microtopics remaining \(([^)]+)\)", query, re.I)
        rem_str = f"{rem_match.group(1)} ({rem_match.group(2)})" if rem_match else "Remaining Microtopics"

        return (
            f"### 📊 Mindset & Syllabus Correlation Diagnostic\n\n"
            f"• **Active Mental State:** `{curr_mood}`\n"
            f"• **Primary Stress Trigger:** `{curr_trigger}`\n"
            f"• **Daily Focus Capacity:** `{energy_str}`\n"
            f"• **Syllabus Navigator Status:** `{comp_str} completed` | `{rem_str} remaining`\n\n"
            f"#### 🔍 Cognitive Load & Energy Audit:\n"
            f"Your current mindset state (**{curr_mood}**) combined with a focus energy score of **{energy_str}** indicates that heavy, uncalibrated 10-hour study marathons will increase anxiety and lower retention. "
            f"With **{rem_str}** in Syllabus Navigator, the key to protecting your mental health while hitting study targets is **Mindset-Calibrated Microtopic Execution**—matching daily target length to active cognitive bandwidth.\n\n"
            f"---\n\n"
            f"### 🗓️ Mindset-Calibrated 7-Day Study Routine & Recovery Plan\n\n"
            f"#### 🟢 **Day 1: De-compression & GS4 Ethics Anchor**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Execute 2 Pomodoro sprints (25 mins each) on **GS4 Ethics: Stress Management & Emotional Intelligence in Public Service**. Soft start builds dopamine.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Complete 2 microtopics of GS2 Polity (Articles 14-19 Fundamental Rights).\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Perform 4-7-8 box breathing for 5 mins. Zero textbook reading post 10:30 PM.\n\n"
            f"#### 🟡 **Day 2: 1-Topic Isolation & GS2 Polity Sprints**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Master 3 microtopics of GS2 Parliament & Legislative Procedures.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Solve 10 UPSC Prelims PYQs on Indian Polity.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** 15-minute outdoor walk without phone.\n\n"
            f"#### 🟠 **Day 3: Mock Panic De-escalation & PYQ Circuit Breaker**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Master 2 microtopics of Modern History (Freedom Struggle 1857-1909).\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Solve 5 PYQs immediately whenever mock test anxiety or negative marking fear arises.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Audit checked-off microtopics in Syllabus Navigator.\n\n"
            f"#### 🔵 **Day 4: Mid-Week Momentum & GS3 Economy Sprints**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Conquering 2 microtopics of GS3 Economy (Inflation & Monetary Policy Instruments).\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Active recall revision of Day 1-3 microtopics using flashcards.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Strict digital DND protocol post 08:30 PM.\n\n"
            f"#### 🟣 **Day 5: Mains Ethics Case Study & Re-framing Exercise**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Write 1 GS4 Ethics Case Study on: *'Maintaining administrative composure during acute stress'*. Convert your personal stressor into case study material.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Master 2 microtopics of GS3 Environment (Biodiversity Conservation).\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Reflection journaling & sleep prep.\n\n"
            f"#### 🟡 **Day 6: Syllabus Progress Audit & Target Consolidation**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Check off completed microtopics in Syllabus Navigator. Reach next target threshold.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Solve 15 mixed Prelims MCQs across GS1 & GS2.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Rest, light reading, and zero overthinking.\n\n"
            f"#### 🟢 **Day 7: Mini Mock Assessment & Mindset Reset**\n"
            f"- **Morning (08:30 AM - 10:00 AM):** 30-minute timed Prelims mini-test (20 MCQs).\n"
            f"- **Afternoon (02:00 PM - 04:00 PM):** Test analysis & updating error log.\n"
            f"- **Evening (07:30 PM - 08:30 PM):** Celebrate completing 7 days of disciplined execution despite mental fatigue!\n\n"
            f"---\n\n"
            f"### 🛡️ 4 Implementable Mindset Safeguard Protocols\n\n"
            f"1. **Calibrated Daily Microtopic Quota:** Short 25/45-min Pomodoro sprints matching your energy level ({energy_str}).\n"
            f"2. **The 1-Topic Isolation Rule:** Focus on 1 single microtopic at a time to halt syllabus panic.\n"
            f"3. **GS4 Ethics Synergy:** Convert your primary stress trigger ({curr_trigger}) into GS4 Ethics study material.\n"
            f"4. **Circadian & Somatic Reset:** 4-7-8 box breathing, 7.5+ hours night sleep, and post-study walk routine."
        )

    def _generate_relationship_syllabus_fallback(self, query: str) -> str:
        rel_match = re.search(r"relationship dynamics is '([^']+)'", query, re.I)
        rel_status = rel_match.group(1) if rel_match else "Relationship Dynamics"

        emo_match = re.search(r"emotional state is '([^']+)'", query, re.I)
        emo_state = emo_match.group(1) if emo_match else "Emotional Distraction"

        drain_match = re.search(r"emotional drain level is (\d+/\d+|\d+)", query, re.I)
        drain_str = drain_match.group(1) if drain_match else "8/10"

        comp_match = re.search(r"completed (\d+) microtopics \(([^)]+)\)", query, re.I)
        comp_str = f"{comp_match.group(1)} ({comp_match.group(2)})" if comp_match else "12 microtopics (1.9%)"

        rem_match = re.search(r"have (\d+) microtopics remaining \(([^)]+)\)", query, re.I)
        rem_str = f"{rem_match.group(1)} ({rem_match.group(2)})" if rem_match else "611 microtopics (98.1%)"

        return (
            f"### 📊 Relationship Dynamics & Syllabus Correlation Analysis\n\n"
            f"• **Relationship Dynamics:** `{rel_status}`\n"
            f"• **Current Emotional State:** `{emo_state}`\n"
            f"• **Emotional Toll Index:** `{drain_str}`\n"
            f"• **Syllabus Navigator Status:** `{comp_str} completed` | `{rem_str} remaining`\n\n"
            f"#### 🔍 Core Cognitive Diagnostic:\n"
            f"An emotional drain level of **{drain_str}** caused by **{rel_status}** triggers acute cognitive fatigue and intrusive overthinking. "
            f"With **{rem_str}** in Syllabus Navigator, attempting 10-hour continuous study marathons will cause rapid burnout. "
            f"To protect your UPSC selection target, your daily execution must be recalibrated into structured 25-minute Pomodoro sprints and strict time-fences.\n\n"
            f"---\n\n"
            f"### 🗓️ Customized 7-Day Actionable Study & Emotional Recovery Plan\n\n"
            f"#### 🟢 **Day 1: De-escalation & GS4 Ethics Anchor**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Execute 2 Pomodoro sprints (25 mins each) on **GS4 Ethics: Emotional Intelligence (EI) & Concept of Human Values**. Low technical cognitive load helps build momentum.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Complete 2 microtopics of GS2 Polity (Articles 14-19 Fundamental Rights).\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Enforce strict 45-min personal check-in window. DND study mode post 08:30 PM.\n\n"
            f"#### 🟡 **Day 2: Boundary Building & GS2 Polity Sprints**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Master 3 microtopics of GS2 Parliament & Legislative Procedures.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Solve 10 UPSC Prelims PYQs on Indian Polity. (Enforce 5-PYQ Circuit Breaker whenever tempted to check personal messages).\n"
            f"- **Evening (07:30 PM - 08:15 PM):** 15-minute outdoor walk + 4-7-8 box breathing.\n\n"
            f"#### 🟠 **Day 3: Cognitive Rechanneling & GS1 Core History**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Master 2 microtopics of Modern History (Freedom Struggle 1857-1909).\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Rechannel unrequited energy/heartbreak into writing 1 Mains 10-marker answer framework.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Audit checked-off microtopics in Syllabus Navigator.\n\n"
            f"#### 🔵 **Day 4: Mid-Week Momentum & GS3 Economy Sprints**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Conquering 2 microtopics of GS3 Economy (Inflation & Monetary Policy Instruments).\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Active recall revision of Day 1-3 microtopics using flashcards.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Strict digital DND protocol post 08:30 PM.\n\n"
            f"#### 🟣 **Day 5: Mains Ethics Case Study & Re-framing Exercise**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Write 1 GS4 Ethics Case Study on: *'Emotional self-regulation under crisis & pressure'*. Use your personal situation as case study material.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Master 2 microtopics of GS3 Environment (Biodiversity Conservation).\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Reflection journaling & sleep prep.\n\n"
            f"#### 🟡 **Day 6: Syllabus Progress Audit & Target Consolidation**\n"
            f"- **Morning (08:30 AM - 11:30 AM):** Check off completed microtopics in Syllabus Navigator. Reach next target threshold.\n"
            f"- **Afternoon (02:00 PM - 05:00 PM):** Solve 15 mixed Prelims MCQs across GS1 & GS2.\n"
            f"- **Evening (07:30 PM - 08:15 PM):** Rest, light reading, and zero overthinking.\n\n"
            f"#### 🟢 **Day 7: Mini Mock Assessment & Mindset Reset**\n"
            f"- **Morning (08:30 AM - 10:00 AM):** 30-minute timed Prelims mini-test (20 MCQs).\n"
            f"- **Afternoon (02:00 PM - 04:00 PM):** Test analysis & updating error log.\n"
            f"- **Evening (07:30 PM - 08:30 PM):** Celebrate completing 7 days of disciplined execution despite emotional drain!\n\n"
            f"---\n\n"
            f"### 🛡️ 4 Implementable Safeguard Protocols\n\n"
            f"1. **Microtopic Execution Quota:** 25-minute Pomodoro sprints for high drain. Do not force 3-hour continuous reading.\n"
            f"2. **The 5-PYQ Circuit Breaker Rule:** Solve 5 PYQs before looking at your personal phone whenever an emotional urge strikes.\n"
            f"3. **GS4 Ethics Synergy:** Treat personal relationship challenges as live GS4 Case Study preparation.\n"
            f"4. **Digital Darkout Schedule:** 08:30 AM to 07:30 PM phone in DND mode."
        )

    def _handle_relationship_syllabus_plan(
        self, query: str, intent_result: IntentResult
    ) -> dict[str, Any]:
        try:
            answer = self._llm_complete(
                query, system_prompt=RELATIONSHIP_SYLLABUS_SYSTEM_PROMPT
            )
            if not answer or len(answer) < 150 or "qa_mental_health_upsc_failure" in answer:
                answer = self._generate_relationship_syllabus_fallback(query)
        except Exception as e:
            print(f"LLM relationship plan error: {e}")
            answer = self._generate_relationship_syllabus_fallback(query)

        return {
            "answer": answer,
            "intent": "relationship_syllabus_7day_plan",
            "category": "non_academic",
            "confidence": "high",
            "mode": "relationship_syllabus_counselor",
            "sources": [],
            "signals": intent_result.signals,
        }

    def chat(self, query: str, mh_count: int = 0, **kwargs) -> dict[str, Any]:
        mh_count = kwargs.get("mh_count", mh_count)
        is_mh_query = False
        intent = "general"
        try:
            intent_result: IntentResult = classify_intent(query)
            intent = intent_result.intent

            is_rel_plan_query = (
                intent == "relationship_syllabus_7day_plan"
                or any(k in query.lower() for k in ("relationship dynamics", "one-sided", "ghosting", "breakup", "unrequited", "mixed signals"))
                or ("relationship" in query.lower() and ("7-day" in query.lower() or "recovery plan" in query.lower() or "microtopic" in query.lower() or "actionable study" in query.lower()))
            )

            if is_rel_plan_query:
                return self._handle_relationship_syllabus_plan(query, intent_result)

            is_mh_query = intent == "mental_health_upsc_distress" or "mental state" in query.lower() or "stress trigger" in query.lower()

            pyqs = self._find_relevant_pyqs(query)
            if pyqs and intent == "general" and not is_mh_query:
                intent = "notes_or_explain_topic"
                intent_result.intent = "notes_or_explain_topic"
                if "academic" not in intent_result.signals:
                    intent_result.signals.append("academic")

            clarification = get_clarification_message(intent)
            if clarification and not is_mh_query:
                return {
                    "answer": clarification,
                    "intent": intent,
                    "category": "non_academic",
                    "confidence": "medium",
                    "sources": [],
                    "mode": "clarification",
                    "signals": intent_result.signals,
                }

            template_intents = {
                "suggest_course_fresh_graduate_only": "qa_course_fresh_grad_only",
                "backup_plan_while_upsc": "qa_backup_plan_upsc_skilling",
            }

            if intent in template_intents:
                record = next(
                    (
                        r
                        for r in self.index.records
                        if r["id"] == template_intents[intent]
                    ),
                    self.index.get_by_intent(intent),
                )
                if record:
                    result = self._template_response(record)
                    result["signals"] = intent_result.signals
                    return result

            if is_mh_query:
                is_syllabus_correlated = "syllabus navigator tracking" in query.lower() or "microtopics" in query.lower() or "mental state" in query.lower()
                sys_prompt = MENTAL_HEALTH_SYLLABUS_SYSTEM_PROMPT if is_syllabus_correlated else NON_ACADEMIC_SYSTEM_PROMPT
                try:
                    answer = self._llm_complete(
                        query if is_syllabus_correlated else f"As a professional psychologist specializing in competitive exam stress, provide specific psychological remedies and actionable coping strategies for this aspirant's concern: {query}. Do NOT suggest PW Skills.",
                        system_prompt=sys_prompt
                    )
                    if not answer or len(answer) < 150 or "qa_mental_health_upsc_failure" in answer:
                        answer = self._generate_mental_health_syllabus_fallback(query)
                except Exception as err:
                    print(f"LLM mental health error: {err}")
                    answer = self._generate_mental_health_syllabus_fallback(query)

                processed_answer = self._postprocess_mental_health_answer(
                    answer, mh_count
                )
                return {
                    "answer": processed_answer,
                    "intent": "mental_health_upsc_distress",
                    "category": "non_academic",
                    "confidence": "high",
                    "sources": [],
                    "mode": "psychologist",
                    "signals": intent_result.signals,
                }

            if intent == "notes_or_explain_topic":
                return self._handle_academic(query, intent_result)

            if intent == "general" and "academic" in intent_result.signals:
                return self._handle_academic(query, intent_result)

            if intent == "general":
                fallback_msg = GENERAL_FALLBACK.format(query=query)
                answer = self._llm_complete(
                    fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT
                )
                return {
                    "answer": answer,
                    "intent": intent,
                    "category": "academic",
                    "confidence": "medium",
                    "sources": [],
                    "mode": "fallback",
                    "signals": intent_result.signals,
                }

            if intent not in ("mental_health_upsc_distress", "relationship_syllabus_7day_plan"):
                record = self.index.get_by_intent(intent)
                if record and record.get("answer_template"):
                    result = self._template_response(record)
                    result["signals"] = intent_result.signals
                    return result

            if "academic" in intent_result.signals or any(
                w in query.lower()
                for w in (
                    "explain",
                    "notes",
                    "causes",
                    "what is",
                    "fundamental rights",
                    "article ",
                    "amendment",
                )
            ):
                return self._handle_academic(query, intent_result)

            fallback_msg = GENERAL_FALLBACK.format(query=query)
            answer = self._llm_complete(
                fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT
            )
            return {
                "answer": answer,
                "intent": intent,
                "category": "academic",
                "confidence": "medium",
                "sources": [],
                "mode": "fallback",
                "signals": intent_result.signals,
            }
        except Exception as e:
            print(f"Chatbot Chat Exception: {e}")
            if is_mh_query or "mental" in query.lower() or "stress" in query.lower():
                ans = self._generate_mental_health_syllabus_fallback(query)
                ans = self._postprocess_mental_health_answer(ans, mh_count)
                return {
                    "answer": ans,
                    "intent": "mental_health_upsc_distress",
                    "category": "non_academic",
                    "confidence": "high",
                    "mode": "psychologist_fallback",
                    "sources": [],
                    "signals": ["mental_health"],
                }

            try:
                fallback_msg = f"Produce a structured UPSC GS answer with Prelims MCQs and Mains practice questions for: {query}"
                ans = self._llm_complete(
                    fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT
                )
                ans = self._ensure_mains_questions(ans, query)
            except Exception:
                ans = self._generate_academic_fallback(query)

            return {
                "answer": ans,
                "intent": (
                    intent
                    if "intent" in locals()
                    else "notes_or_explain_topic"
                ),
                "category": "academic",
                "confidence": "medium",
                "mode": "fallback",
                "sources": [],
                "signals": (
                    intent_result.signals
                    if "intent_result" in locals()
                    else ["academic"]
                ),
            }

            try:
                fallback_msg = f"Produce a structured UPSC GS answer with Prelims MCQs and Mains practice questions for: {query}"
                ans = self._llm_complete(
                    fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT
                )
                ans = self._ensure_mains_questions(ans, query)
            except Exception:
                ans = self._generate_academic_fallback(query)

            return {
                "answer": ans,
                "intent": (
                    intent
                    if "intent" in locals()
                    else "notes_or_explain_topic"
                ),
                "category": "academic",
                "confidence": "medium",
                "mode": "fallback",
                "sources": [],
                "signals": (
                    intent_result.signals
                    if "intent_result" in locals()
                    else ["academic"]
                ),
            }
