from __future__ import annotations

from typing import Any, Optional

from config import LLM_MODEL, get_groq_client
from generation.prompts import ACADEMIC_USER_TEMPLATE, GENERAL_FALLBACK, SYSTEM_PROMPT
from ingestion.indexer import VectorIndex, load_index
from retrieval.intent_router import (
    IntentResult,
    classify_intent,
    get_clarification_message,
)


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
            max_tokens=1500,
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

    def _academic_response(self, query: str, record: dict, score: float) -> dict[str, Any]:
        meta = record.get("metadata", {})
        user_msg = ACADEMIC_USER_TEMPLATE.format(
            query=query,
            topic=meta.get("syllabus_topic", record.get("question", "")),
            subject=meta.get("subject", "General Studies"),
            content=record.get("answer_content", record.get("answer_template", "")),
        )
        answer = self._llm_complete(user_msg)
        confidence = "high" if score >= 0.15 else "medium"
        return {
            "answer": answer,
            "intent": "notes_or_explain_topic",
            "category": "academic",
            "confidence": confidence,
            "sources": [{"id": record["id"], "question": record["question"], "score": score}],
            "mode": "rag",
        }

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

        if intent == "notes_or_explain_topic" or intent == "general":
            results = self.index.search(query, top_k=3, category="academic")
            if results and results[0]["score"] >= 0.05:
                best = results[0]
                result = self._academic_response(query, best["record"], best["score"])
                result["signals"] = intent_result.signals
                return result

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
