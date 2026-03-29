"""FastAPI endpoints for the VectixLogic policy RAG service."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from api.root_page import load_root_page

app = FastAPI(title="VectixLogic Policy RAG API")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks: list[dict]


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Serve the required web chat interface at the root path."""
    return HTMLResponse(content=load_root_page())


@app.get("/health")
def health() -> dict[str, str]:
    """Lightweight health check."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Execute RAG question answering for a user query."""
    from src.rag_app import get_engine

    engine = get_engine()
    result = engine.ask(req.query.strip() or "What are the core hours?", k=4)
    return ChatResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        chunks=result.get("chunks", []),
    )
