from __future__ import annotations

from typing import Optional


EXAM_SEARCH_SUFFIXES = {
    "UPSC": "UPSC civil services exam notes",
    "IIT-JEE": "IIT JEE Main Advanced Physics Chemistry Math notes solution",
    "NEET": "NEET medical entrance NCERT Biology Chemistry Physics notes",
    "GATE": "GATE engineering exam notes concepts formulas",
    "CAT": "CAT exam Quantitative Aptitude DILR VARC concepts notes",
    "Banking": "Banking SBI PO IBPS Quant Reasoning General Awareness notes",
    "SSC": "SSC CGL CHSL Reasoning Quant English GA notes",
}


def search_exam_topic(query: str, exam_vertical: str = "UPSC", max_results: int = 5) -> list[dict]:
    """Search the web for exam-oriented content on a topic."""
    suffix = EXAM_SEARCH_SUFFIXES.get(exam_vertical, "exam notes")
    search_query = f"{query} {suffix}"
    results = []

    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            for item in ddgs.text(search_query, max_results=max_results):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "snippet": item.get("body", ""),
                        "url": item.get("href", ""),
                    }
                )
    except Exception as exc:
        results.append(
            {
                "title": "Search unavailable",
                "snippet": f"Web search could not be completed: {exc}",
                "url": "",
            }
        )

    return results


def search_upsc_topic(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for UPSC-oriented content on a topic (backward compatible)."""
    return search_exam_topic(query, exam_vertical="UPSC", max_results=max_results)



def format_web_context(results: list[dict]) -> str:
    if not results:
        return "No web results found."

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r.get('title', 'Untitled')}\n"
            f"Source: {r.get('url', 'N/A')}\n"
            f"{r.get('snippet', '')}"
        )
    return "\n\n".join(parts)
