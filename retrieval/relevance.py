from __future__ import annotations

import re


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]{4,}", text.lower())
    stop = {
        "explain",
        "notes",
        "what",
        "about",
        "indian",
        "india",
        "upsc",
        "prelims",
        "mains",
        "provide",
        "causes",
        "cause",
        "topic",
        "describe",
    }
    return {w for w in words if w not in stop}


def is_kb_relevant(query: str, record: dict, score: float, min_score: float = 0.15) -> bool:
    """Only use knowledge-base context when retrieval is genuinely on-topic."""
    if score < min_score:
        return False

    record_text = " ".join(
        [
            record.get("question", ""),
            " ".join(record.get("question_variants", [])),
            record.get("metadata", {}).get("syllabus_topic", ""),
            record.get("answer_content", "")[:200],
        ]
    )

    query_kw = _keywords(query)
    record_kw = _keywords(record_text)
    if not query_kw:
        return score >= 0.35

    overlap = query_kw & record_kw
    return len(overlap) >= 1
