import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure we can import from phase2_rag
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.phase2_rag.pipeline import ask_assistant

app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Stateless RAG API serving verified facts about HDFC Mutual Funds.",
    version="1.0.0"
)

# Allow CORS for local development (Phase 3.2 frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional

# Schemas
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    source: Optional[str] = None
    footer: Optional[str] = None

@app.get("/health")
def health_check():
    """Returns the health status of the API."""
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Stateless chat endpoint. Processes the query through the RAG pipeline
    and returns the factual response without storing session data.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        # Call the RAG pipeline directly
        result = ask_assistant(request.query)
        return ChatResponse(
            answer=result.get("answer"),
            source=result.get("source"),
            footer=result.get("footer")
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing the request.")

if __name__ == "__main__":
    import uvicorn
    # When run directly, start the uvicorn server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
