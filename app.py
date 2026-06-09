import streamlit as st

from generation.rag_chain import RAGChatbot

st.set_page_config(page_title="UPSC RAG Mentor", page_icon="📚", layout="centered")

st.title("UPSC RAG Mentor")
st.caption("Course guidance · Backup plans · Mental health support · Academic notes (web-augmented)")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = RAGChatbot()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            with st.expander("Details"):
                st.json(msg["meta"])

if prompt := st.chat_input("Ask about UPSC prep, topics, backup plans..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.chatbot.chat(prompt)
        st.markdown(result["answer"])
        meta = {
            "intent": result["intent"],
            "category": result["category"],
            "confidence": result["confidence"],
            "mode": result["mode"],
            "signals": result.get("signals", []),
            "sources": result.get("sources", []),
        }
        with st.expander("Details"):
            st.json(meta)

    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "meta": meta}
    )
