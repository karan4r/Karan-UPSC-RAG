from fastapi import FastAPI
from pydantic import BaseModel

from generation.rag_chain import RAGChatbot

app = FastAPI(title="UPSC RAG Chatbot", version="1.0.0")
chatbot = RAGChatbot()


class ChatRequest(BaseModel):
    message: str
    exam_vertical: str = "UPSC"


class ChatResponse(BaseModel):
    answer: str
    intent: str
    category: str
    confidence: str
    mode: str
    sources: list
    signals: list = []
    exam_vertical: str = "UPSC"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = chatbot.chat(request.message.strip(), exam_vertical=request.exam_vertical)
    return ChatResponse(
        answer=result["answer"],
        intent=result["intent"],
        category=result["category"],
        confidence=result["confidence"],
        mode=result["mode"],
        sources=result.get("sources", []),
        signals=result.get("signals", []),
        exam_vertical=result.get("exam_vertical", request.exam_vertical),
    )

