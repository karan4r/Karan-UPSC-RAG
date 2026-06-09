from __future__ import annotations

from typing import Any, Optional

from config import LLM_MODEL, get_groq_client
from generation.prompts import (
    ACADEMIC_LLM_FALLBACK_TEMPLATE,
    ACADEMIC_USER_TEMPLATE,
    ACADEMIC_WEB_ONLY_TEMPLATE,
    GENERAL_FALLBACK,
    SYSTEM_PROMPT,
)
from ingestion.indexer import VectorIndex, load_index
from retrieval.intent_router import (
    IntentResult,
    classify_intent,
    get_clarification_message,
)
from retrieval.relevance import is_kb_relevant
from retrieval.web_search import format_web_context, search_upsc_topic


class RAGChatbot:
    def __init__(self, index: Optional[VectorIndex] = None):
        self.index = index or load_index()
        self.client = get_groq_client()

    def _llm_complete(self, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""

    def _template_response(self, record: dict) -> dict[str, Any]:
        return {
            "answer": record["answer_template"],
            "intent": record["intent"],
            "category": record["category"],
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

        answer = self._llm_complete(user_msg)
        return {
            "answer": answer,
            "intent": "notes_or_explain_topic",
            "category": "academic",
            "confidence": confidence,
            "sources": sources,
            "mode": mode,
        }

    def _handle_academic(self, query: str, intent_result: IntentResult) -> dict[str, Any]:
        results = self.index.search(query, top_k=1, category="academic")
        rag_record = results[0]["record"] if results else None
        rag_score = results[0]["score"] if results else 0.0

        result = self._academic_response(query, rag_record, rag_score)
        result["signals"] = intent_result.signals
        return result

    def chat(self, query: str) -> dict[str, Any]:
        intent_result: IntentResult = classify_intent(query)
        intent = intent_result.intent

        clarification = get_clarification_message(intent)
        if clarification:
            return {
                "answer": clarification,
                "intent": intent,
                "category": "course_recommendation",
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
                return result

        if intent == "notes_or_explain_topic":
            return self._handle_academic(query, intent_result)

        if intent == "general" and "academic" in intent_result.signals:
            return self._handle_academic(query, intent_result)

        if intent == "general":
            fallback_msg = GENERAL_FALLBACK.format(query=query)
            answer = self._llm_complete(fallback_msg)
            return {
                "answer": answer,
                "intent": intent,
                "category": "general",
                "confidence": "low",
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
            w in query.lower() for w in ("explain", "notes", "causes", "what is")
        ):
            return self._handle_academic(query, intent_result)

        fallback_msg = GENERAL_FALLBACK.format(query=query)
        answer = self._llm_complete(fallback_msg)
        return {
            "answer": answer,
            "intent": intent,
            "category": "general",
            "confidence": "low",
            "sources": [],
            "mode": "fallback",
            "signals": intent_result.signals,
        }
