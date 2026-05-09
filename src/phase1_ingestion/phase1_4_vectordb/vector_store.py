import os
import sys
import hashlib
import chromadb
from chromadb.config import Settings

# Directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, "data", "chroma_db")

# Add the project root to sys.path to import from phase1_3_chunking
sys.path.append(PROJECT_ROOT)
from src.phase1_ingestion.phase1_3_chunking.chunker import load_and_chunk_documents, embed_chunks

def get_chroma_client():
    if not os.path.exists(CHROMA_DB_DIR):
        os.makedirs(CHROMA_DB_DIR)
        print(f"Created Chroma DB directory: {CHROMA_DB_DIR}")
        
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    return client

def populate_database():
    print("Loading and chunking documents...")
    chunks = load_and_chunk_documents()
    if not chunks:
        print("No chunks found. Ensure Phase 1.2 and 1.3 are complete.")
        return
        
    print("Generating embeddings...")
    embeddings = embed_chunks(chunks)
    
    print("Initializing ChromaDB...")
    client = get_chroma_client()
    
    # We use cosine similarity (which maps well to sentence-transformers)
    collection_name = "mutual_fund_faqs"
    
    # Delete existing if we want a fresh start, or we can just get_or_create
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}' to start fresh.")
    except ValueError:
        pass
        
    collection = client.create_collection(
        name=collection_name, 
        metadata={"hnsw:space": "cosine"}
    )
    
    print(f"Populating collection '{collection_name}'...")
    
    docs = []
    metadatas = []
    ids = []
    embs = []
    
    for i, chunk in enumerate(chunks):
        content = chunk.page_content
        metadata = chunk.metadata
        
        # Flatten metadata to simple string values for Chroma
        flat_metadata = {}
        section_parts = []
        
        for k, v in metadata.items():
            if k == 'Source URL':
                flat_metadata['source_url'] = str(v)
            elif k == 'Fund Name':
                flat_metadata['scheme_name'] = str(v)
            elif k in ['Header 1', 'Header 2', 'Header 3', 'Header 4', 'Section', 'Subsection', 'Detail']:
                section_parts.append(str(v))
        
        if section_parts:
            flat_metadata['section_header'] = " > ".join(section_parts)
        else:
            flat_metadata['section_header'] = "General"
            
        if 'scheme_name' not in flat_metadata:
             flat_metadata['scheme_name'] = "Unknown Scheme"
             
        # Create a unique ID using a hash of the content so it's idempotent
        chunk_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        chunk_id = f"chunk_{i}_{chunk_hash[:8]}"
        
        docs.append(content)
        metadatas.append(flat_metadata)
        ids.append(chunk_id)
        # Convert numpy array to list for Chroma
        embs.append(embeddings[i].tolist())
        
    collection.add(
        documents=docs,
        metadatas=metadatas,
        ids=ids,
        embeddings=embs
    )
    
    print(f"Successfully added {len(docs)} chunks to the database!")
    return collection

def test_query(collection):
    print("\n--- Running Test Query ---")
    query_text = "What is the exit load?"
    print(f"Query: '{query_text}'")
    
    # We must generate the embedding for the query using the exact same model
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query_text])[0].tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    for i in range(len(results['documents'][0])):
        print(f"\nResult {i+1}:")
        print(f"Metadata: {results['metadatas'][0][i]}")
        print(f"Distance (Cosine): {results['distances'][0][i]}")
        snippet = results['documents'][0][i].strip()[:150].replace('\n', ' ')
        print(f"Content Snippet: {snippet}...")

if __name__ == "__main__":
    collection = populate_database()
    if collection:
        test_query(collection)
