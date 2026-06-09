import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def _get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


LLM_PROVIDER = _get_secret("LLM_PROVIDER", "groq")
LLM_MODEL = _get_secret("LLM_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = _get_secret("GROQ_API_KEY", "")


def get_groq_client():
    from groq import Groq

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to .env locally or "
            "Streamlit Cloud Secrets (Settings → Secrets)."
        )

    return Groq(api_key=GROQ_API_KEY)
