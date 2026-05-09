import os
import sys
import chromadb
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

# Directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, "data", "chroma_db")

# Ensure phase 1 paths are accessible
sys.path.append(PROJECT_ROOT)

def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    return client.get_collection("mutual_fund_faqs")

def extract_metadata_filters(query: str, llm):
    """Uses an LLM to extract the scheme_name from the user query."""
    
    parser = JsonOutputParser()
    
    prompt = PromptTemplate(
        template="""You are an expert financial router. Extract the mutual fund scheme name from the user's query if present.
        We only have data for the following funds:
        1. HDFC Mid Cap Fund Direct Growth
        2. HDFC Flexi Cap Direct Plan Growth (also known as HDFC Equity Fund)
        3. HDFC Focused Fund Direct Growth
        4. HDFC ELSS Tax Saver Fund Direct Plan Growth
        5. HDFC Large Cap Fund Direct Growth
        
        If the user mentions one of these, or a close variation (e.g., 'hdfc mid cap'), output the exact official scheme name from the list above.
        If no fund is clearly mentioned, output null for scheme_name.
        
        Format your response as a valid JSON object matching this schema:
        {{
            "scheme_name": "Official Scheme Name or null"
        }}
        
        Query: {query}
        """,
        input_variables=["query"]
    )
    
    chain = prompt | llm | parser
    try:
        result = chain.invoke({"query": query})
        return result.get("scheme_name")
    except Exception as e:
        print(f"Failed to extract metadata filter: {e}")
        return None

def retrieve_context(query: str, llm):
    """Retrieves the most relevant chunks from ChromaDB, pre-filtered by scheme_name."""
    
    # 1. Self-Query / Metadata Extraction
    scheme_name = extract_metadata_filters(query, llm)
    print(f"[Retriever] Extracted Target Scheme: {scheme_name}")
    
    # 2. Build ChromaDB Filter
    where_filter = None
    if scheme_name:
        where_filter = {"scheme_name": scheme_name}
        
    # 3. Generate Embedding for the Query
    from sentence_transformers import SentenceTransformer
    emb_model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = emb_model.encode([query])[0].tolist()
    
    # 4. Perform Vector Search
    collection = get_chroma_collection()
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=where_filter
        )
    except Exception as e:
        print(f"[Retriever] Error querying ChromaDB: {e}")
        return []
        
    documents = results['documents'][0] if results['documents'] else []
    metadatas = results['metadatas'][0] if results['metadatas'] else []
    distances = results['distances'][0] if results['distances'] else []
    
    retrieved_chunks = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        # We can implement a distance threshold fallback here
        if dist < 1.0: # Cosine distance threshold (lower is closer)
            retrieved_chunks.append({
                "content": doc,
                "metadata": meta,
                "distance": dist
            })
            
    return retrieved_chunks

if __name__ == "__main__":
    # Test script
    # Assumes GROQ_API_KEY is in environment
    if not os.getenv("GROQ_API_KEY"):
        print("Please set GROQ_API_KEY in environment to test.")
    else:
        test_llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
        chunks = retrieve_context("What is the exit load for HDFC Mid Cap?", test_llm)
        print(f"Found {len(chunks)} chunks.")
        if chunks:
            print(chunks[0]['metadata'])
