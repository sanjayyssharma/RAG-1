import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.phase2_rag.retriever import retrieve_context
from src.phase2_rag.generator import generate_answer

load_dotenv()

def ask_assistant(query: str):
    """Orchestrates the entire Phase 2 RAG pipeline."""
    
    # 1. Initialize LLM (Ensure GROQ_API_KEY is set)
    if not os.getenv("GROQ_API_KEY"):
        return {
            "answer": "System Error: GROQ_API_KEY is not set. Please add it to the environment variables.",
            "source": None,
            "footer": None
        }
        
    # We use a 0 temperature model for deterministic, factual extraction and generation
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    
    # 2. Retrieve Context (Self-Query + Metadata Filter + Semantic Search)
    print(f"\n[Pipeline] Processing Query: '{query}'")
    retrieved_chunks = retrieve_context(query, llm)
    
    if retrieved_chunks:
        print(f"[Pipeline] Retrieved {len(retrieved_chunks)} relevant chunks from Vector DB.")
    else:
        print("[Pipeline] No relevant context found.")
        
    # 3. Generate Answer (PII filter, Strict prompt)
    response_data = generate_answer(query, retrieved_chunks, llm)
    
    # 4. Construct Final Footer
    footer = None
    if response_data.get("source"):
        date_str = datetime.now().strftime("%d %b %Y")
        footer = f"Last updated from sources: {date_str}"
        
    return {
        "answer": response_data["answer"],
        "source": response_data.get("source"),
        "footer": footer
    }

if __name__ == "__main__":
    # Test Queries
    test_queries = [
        "What is the exit load for HDFC Flexi Cap?",
        "Should I invest my money in HDFC Mid Cap?",
        "My PAN is ABCDE1234F, what is the NAV of HDFC Large Cap?"
    ]
    
    print("=== Phase 2 RAG Pipeline Test ===")
    for q in test_queries:
        res = ask_assistant(q)
        print("\n---")
        print(f"User: {q}")
        print(f"Assistant: {res['answer']}")
        if res['source']:
            print(f"Source: {res['source']}")
        if res['footer']:
            print(f"{res['footer']}")
    print("\n=================================")
