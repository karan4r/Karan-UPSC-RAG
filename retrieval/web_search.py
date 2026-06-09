from __future__ import annotations

from typing import Optional


def search_upsc_topic(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for UPSC-oriented content on a topic."""
    search_query = f"{query} UPSC civil services exam notes"
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
