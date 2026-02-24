"""
FastAPI: /health and /chat for VectixLogic Policy RAG.

Run: uvicorn api.main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="VectixLogic Policy RAG API")


@app.get("/")
def root():
    """Root endpoint: API info and links."""
    return {
        "service": "VectixLogic Policy RAG API",
        "docs": "/docs",
        "health": "/health",
        "chat": "POST /chat",
    }


@app.get("/health")
def health():
    """Health check for deployment and load balancers."""
    return {"status": "ok"}


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks: list[dict]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """RAG chat: returns answer and source identifiers/snippets."""
    from src.rag_app import get_engine
    engine = get_engine()
    result = engine.ask(req.query.strip() or "What are the core hours?", k=4)
    return ChatResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        chunks=result.get("chunks", []),
    )
