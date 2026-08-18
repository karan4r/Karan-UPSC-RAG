import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


DEPRECATED_MODELS = {
    "llama3-70b-8192",
    "llama-3.3-70b-specdec",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
}


def _get_secret(key: str, default: str = "") -> str:
    val = default
    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
    except Exception:
        val = os.getenv(key, default)

    if not val:
        val = os.getenv(key, default)

    if key == "LLM_MODEL" and val in DEPRECATED_MODELS:
        return default
    return val


LLM_PROVIDER = _get_secret("LLM_PROVIDER", "groq")
LLM_MODEL = _get_secret("LLM_MODEL", "openai/gpt-oss-120b")
LLM_FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "groq/compound",
    "groq/compound-mini",
    "qwen/qwen3.6-27b",
]
GROQ_API_KEY = _get_secret("GROQ_API_KEY", "")


def get_groq_client():
    from groq import Groq

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to .env locally or "
            "Streamlit Cloud Secrets (Settings → Secrets)."
        )

    return Groq(api_key=GROQ_API_KEY)
