from __future__ import annotations

from typing import Any, Optional

from config import LLM_MODEL, LLM_FALLBACK_MODELS, get_groq_client
from generation.prompts import (
    ACADEMIC_LLM_FALLBACK_TEMPLATE,
    ACADEMIC_SYSTEM_PROMPT,
    ACADEMIC_USER_TEMPLATE,
    ACADEMIC_WEB_ONLY_TEMPLATE,
    GENERAL_FALLBACK,
    NON_ACADEMIC_SYSTEM_PROMPT,
)
from ingestion.indexer import VectorIndex, load_index
from retrieval.intent_router import (
    IntentResult,
    classify_intent,
    get_clarification_message,
)
from retrieval.relevance import is_kb_relevant
from retrieval.web_search import format_web_context, search_upsc_topic

import json
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RAGChatbot:
    def __init__(self, index: Optional[VectorIndex] = None):
        self.index = index or load_index()
        self.client = get_groq_client()
        self.pyq_path = Path(__file__).resolve().parent.parent / "data" / "modern_history_pyqs.json"
        self.pyqs = []
        if self.pyq_path.exists():
            with open(self.pyq_path, encoding="utf-8") as f:
                self.pyqs = json.load(f)

    def _llm_complete(self, user_message: str, system_prompt: str = ACADEMIC_SYSTEM_PROMPT) -> str:
        models_to_try = [LLM_MODEL] + [m for m in LLM_FALLBACK_MODELS if m != LLM_MODEL]
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
                content = re.sub(r"^<think>.*?</think>\s*", "", content, flags=re.DOTALL)
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
            texts.append(f"{pyq.get('question', '')} {pyq.get('explanation', '')}")
            
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform(texts)
            query_vec = vectorizer.transform([query])
            scores = cosine_similarity(query_vec, matrix).flatten()
            
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
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
            "category": "non_academic" if record.get("category") != "academic" else "academic",
            "confidence": "high",
            "sources": [{"id": record["id"], "question": record["question"]}],
            "mode": "template",
        }

    def _build_kb_context(self, record: Optional[dict]) -> str:
        if not record:
            return "No matching entry in local knowledge base."
        meta = record.get("metadata", {})
        content = record.get("answer_content") or record.get("answer_template", "")
        return (
            f"Topic: {meta.get('syllabus_topic', record.get('question', ''))}\n"
            f"Subject: {meta.get('subject', 'General Studies')}\n"
            f"Content: {content}"
        )

    def _web_results_usable(self, web_results: list[dict]) -> bool:
        if not web_results:
            return False
        if len(web_results) == 1 and web_results[0].get("title") == "Search unavailable":
            return False
        return any(r.get("snippet") for r in web_results)

    def _academic_response(
        self,
        query: str,
        rag_record: Optional[dict] = None,
        rag_score: float = 0.0,
        web_results: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        web_results = web_results if web_results is not None else search_upsc_topic(query)
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
                {"id": rag_record["id"], "question": rag_record["question"], "score": rag_score},
                *[{"title": r["title"], "url": r["url"]} for r in web_results[:3] if r.get("url")],
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

        answer = self._llm_complete(user_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT)
        answer = self._ensure_prelims_questions(answer, query)
        answer = self._ensure_mains_questions(answer, query)

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

    def _ensure_prelims_questions(self, answer: str, query: str) -> str:
        if "Prelims Practice Questions" in answer or "Practice MCQs" in answer or "Question 1:" in answer or "📝" in answer:
            return answer

        clean_q = re.sub(r"^(explain|notes on|what is|describe)\s+", "", query, flags=re.I).strip()
        topic = clean_q.capitalize() if clean_q else query

        prelims_block = (
            f"\n\n### 📝 Practice MCQs & UPSC Prelims Questions\n\n"
            f"**Question 1:** With reference to **{topic}**, consider the following statements:\n"
            f"1. It forms an essential component of the UPSC General Studies syllabus framework.\n"
            f"2. Comprehensive analysis requires integrating statutory provisions with recent policy developments.\n"
            f"Which of the statements given above is/are correct?\n"
            f"- **A)** 1 only\n"
            f"- **B)** 2 only\n"
            f"- **C)** Both 1 and 2\n"
            f"- **D)** Neither 1 nor 2\n\n"
            f"**Correct Answer:** Option **C**\n"
            f"**Explanation:** Both statements are correct. UPSC Civil Services examination requires evaluating core concepts alongside contemporary policy developments.\n\n"
            f"**Question 2:** Which of the following best reflects the primary objective of studying **{topic}** for UPSC?\n"
            f"- **A)** Isolated rote learning\n"
            f"- **B)** Developing multi-dimensional conceptual clarity for GS answer writing\n"
            f"- **C)** Technical specialization in non-syllabus areas\n"
            f"- **D)** None of the above\n\n"
            f"**Correct Answer:** Option **B**\n"
            f"**Explanation:** UPSC evaluates candidates on analytical synthesis, policy awareness, and structured answer writing."
        )
        return answer.strip() + prelims_block

    def _ensure_mains_questions(self, answer: str, query: str) -> str:
        if "Mains Practice Questions" in answer or "Mains Question" in answer or "✍️" in answer:
            return answer
        
        clean_q = re.sub(r"^(explain|notes on|what is|describe)\s+", "", query, flags=re.I).strip()
        topic = clean_q.capitalize() if clean_q else query

        mains_block = (
            f"\n\n### ✍️ UPSC Mains Practice Questions\n\n"
            f"**Mains Question 1 (10 Marks / 150 Words):**\n"
            f"\"Critically analyze the core dimensions and significance of **{topic}** in contemporary Indian governance.\"\n\n"
            f"- **Answer Writing Approach:**\n"
            f"  - **Introduction:** Briefly define {topic} and contextualize its syllabus relevance (2 lines).\n"
            f"  - **Core Body Points:** Highlight key structural aspects, constitutional/statutory links, and challenges.\n"
            f"  - **Conclusion / Way Forward:** Provide a balanced, forward-looking concluding observation.\n\n"
            f"**Mains Question 2 (15 Marks / 250 Words):**\n"
            f"\"Discuss the major challenges associated with **{topic}**. What policy and institutional reforms are needed to address these effectively?\"\n\n"
            f"- **Answer Writing Approach:**\n"
            f"  - **Introduction:** Contextual background of {topic}.\n"
            f"  - **Core Body Points:** Multi-dimensional analysis (Administrative, Legal, Socio-Economic) + Committee references.\n"
            f"  - **Conclusion / Way Forward:** Actionable policy recommendations for sustainable outcomes."
        )
        return answer.strip() + mains_block

    def _generate_academic_fallback(self, query: str) -> str:
        clean_q = re.sub(r"^(explain|notes on|what is|describe)\s+", "", query, flags=re.I).strip()
        title = clean_q.capitalize() if clean_q else query
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

    def _handle_academic(self, query: str, intent_result: IntentResult) -> dict[str, Any]:
        results = self.index.search(query, top_k=1, category="academic")
        rag_record = results[0]["record"] if results else None
        rag_score = results[0]["score"] if results else 0.0

        result = self._academic_response(query, rag_record, rag_score)
        result["signals"] = intent_result.signals
        return result

    def _postprocess_mental_health_answer(self, answer: str, mh_count: int) -> str:
        lines = [line for line in answer.splitlines() if "pwskills" not in line.lower() and "pw skills" not in line.lower()]
        answer = "\n".join(lines)
        
        helpline_pattern = r'(?s)---\s*\n### 📞 \*\*24/7 Confidential Professional Support Lines.*?(?=---\s*\n🤗|\Z)'
        
        if mh_count > 0:
            answer = re.sub(helpline_pattern, '', answer)
            
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

    def chat(self, query: str, mh_count: int = 0, **kwargs) -> dict[str, Any]:
        mh_count = kwargs.get("mh_count", mh_count)
        is_mh_query = False
        intent = "general"
        try:
            intent_result: IntentResult = classify_intent(query)
            intent = intent_result.intent

            is_mh_query = (intent == "mental_health_upsc_distress")

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
                "mental_health_upsc_distress": "qa_mental_health_upsc_failure",
                "suggest_course_fresh_graduate_only": "qa_course_fresh_grad_only",
                "backup_plan_while_upsc": "qa_backup_plan_upsc_skilling",
            }

            if intent in template_intents:
                record = next(
                    (r for r in self.index.records if r["id"] == template_intents[intent]),
                    self.index.get_by_intent(intent),
                )
                if record:
                    result = self._template_response(record)
                    result["signals"] = intent_result.signals
                    if is_mh_query:
                        result["answer"] = self._postprocess_mental_health_answer(result["answer"], mh_count)
                    return result

            if is_mh_query:
                fallback_msg = f"As a professional psychologist specializing in competitive exam stress, provide specific psychological remedies and actionable coping strategies for this aspirant's concern: {query}. Do NOT suggest PW Skills."
                answer = self._llm_complete(fallback_msg, system_prompt=NON_ACADEMIC_SYSTEM_PROMPT)
                processed_answer = self._postprocess_mental_health_answer(answer, mh_count)
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
                answer = self._llm_complete(fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT)
                return {
                    "answer": answer,
                    "intent": intent,
                    "category": "academic",
                    "confidence": "medium",
                    "sources": [],
                    "mode": "fallback",
                    "signals": intent_result.signals,
                }

            record = self.index.get_by_intent(intent)
            if record and record.get("answer_template"):
                result = self._template_response(record)
                result["signals"] = intent_result.signals
                return result

            if "academic" in intent_result.signals or any(
                w in query.lower() for w in ("explain", "notes", "causes", "what is", "fundamental rights", "article ", "amendment")
            ):
                return self._handle_academic(query, intent_result)

            fallback_msg = GENERAL_FALLBACK.format(query=query)
            answer = self._llm_complete(fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT)
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
            if is_mh_query:
                ans = (
                    "🩺 **Professional Psychological Assessment & Clinical Remedies**\n\n"
                    "High-stakes competitive exam preparation can trigger acute performance stress, cognitive fatigue, and existential anxiety. As a professional psychologist, I want to assure you that your emotional distress is a natural neuro-biological response to sustained pressure — not a personal flaw.\n\n"
                    "---\n\n"
                    "### 🧠 **Specific Evidence-Based Psychological Remedies**\n\n"
                    "1. **Cognitive Behavioral Reframing (Decoupling Identity from Results)**\n"
                    "   - *Psychological Insight:* UPSC is an elimination test, not an evaluation of your intrinsic worth or intelligence.\n"
                    "   - *Actionable Remedy:* Reframe thoughts of failure to *'I am undergoing a high-attrition selection process. My intellect and value remain intact outside CSE cutoffs.'*\n\n"
                    "2. **Somatic Cortisol Reduction (4-7-8 Vagus Nerve Activation)**\n"
                    "   - *Psychological Insight:* Acute anxiety floods the body with cortisol and adrenaline.\n"
                    "   - *Actionable Remedy:* Inhale through nose for 4s, hold for 7s, exhale for 8s. Perform 4 cycles twice daily.\n\n"
                    "3. **Circadian & Cognitive Hygiene (The 90-Minute Focus Protocol)**\n"
                    "   - *Psychological Insight:* Studying beyond 90 continuous minutes creates cognitive saturation.\n"
                    "   - *Actionable Remedy:* Enforce non-negotiable 15-minute disconnect breaks after every 90 minutes of intensive study."
                )
                ans = self._postprocess_mental_health_answer(ans, mh_count)
                return {
                    "answer": ans,
                    "intent": "mental_health_upsc_distress",
                    "category": "non_academic",
                    "confidence": "high",
                    "mode": "psychologist_fallback",
                    "sources": [],
                    "signals": ["mental_health"]
                }
            
            try:
                fallback_msg = f"Produce a structured UPSC GS answer with Prelims MCQs and Mains practice questions for: {query}"
                ans = self._llm_complete(fallback_msg, system_prompt=ACADEMIC_SYSTEM_PROMPT)
                ans = self._ensure_mains_questions(ans, query)
            except Exception:
                ans = self._generate_academic_fallback(query)
            
            return {
                "answer": ans,
                "intent": intent if 'intent' in locals() else "notes_or_explain_topic",
                "category": "academic",
                "confidence": "medium",
                "mode": "fallback",
                "sources": [],
                "signals": intent_result.signals if 'intent_result' in locals() else ["academic"]
            }
