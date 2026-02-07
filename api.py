#!/usr/bin/env python3
"""
FAST API server for the podcast chatbot.
Provides REST endpoints for querying the chatbot.

Install with: pip install fastapi uvicorn
Run with: uvicorn api.py --reload
"""

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    from pathlib import Path
except ImportError:
    print("FastAPI not installed. Install with: pip install fastapi uvicorn")
    exit(1)


from chatbot import PodcastChatbot
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Podbotnik API",
    description="RAG-powered podcast chatbot API",
    version="1.0.0",
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = None


class Question(BaseModel):
    """Request model for questions."""
    question: str


class Answer(BaseModel):
    """Response model for answers."""
    answer: str
    sources: list
    context_used: int


@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on startup."""
    global chatbot
    
    transcripts_file = os.getenv("TRANSCRIPTS_FILE", "sample_transcripts.json")
    
    if not Path(transcripts_file).exists():
        print(f"⚠️  Transcripts file not found: {transcripts_file}")
        raise Exception(f"Transcripts file not found: {transcripts_file}")
    
    try:
        chatbot = PodcastChatbot()
        chatbot.load_transcripts(transcripts_file)
        print(f"✅ Loaded {len(chatbot.list_episodes())} episode(s)")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        raise


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Podbotnik API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "episodes": "/api/episodes",
            "ask": "/api/ask",
            "docs": "/docs",
        },
    }


@app.get("/api/episodes")
async def get_episodes():
    """Get list of all episodes."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    return {
        "episodes": chatbot.list_episodes(),
        "count": len(chatbot.list_episodes()),
    }


@app.post("/api/ask", response_model=Answer)
async def ask_question(request: Question, max_context_segments: int = 3):
    """Answer a question about the podcast.
    
    Query parameters:
        max_context_segments: Number of transcript segments to use (default: 3)
    """
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = chatbot.answer_question(
            question=request.question,
            max_context_segments=max_context_segments,
        )
        return Answer(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search_transcripts(query: str, max_results: int = 5):
    """Search transcripts directly."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = chatbot.index.search(
        query=query,
        fields=["episode_title", "text"],
        max_results=max_results,
    )
    
    return {
        "query": query,
        "results": results,
        "count": len(results),
    }


if __name__ == "__main__":
    print("🚀 Starting Podbotnik API Server...")
    print("📖 API Docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
