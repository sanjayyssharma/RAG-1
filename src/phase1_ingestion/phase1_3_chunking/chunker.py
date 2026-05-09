import os
from langchain_text_splitters import MarkdownHeaderTextSplitter
from sentence_transformers import SentenceTransformer

# Directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")

# Define the headers to split on
headers_to_split_on = [
    ("#", "Fund Name"),
    ("##", "Section"),
    ("###", "Subsection"),
    ("####", "Detail")
]

def load_and_chunk_documents():
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    all_chunks = []
    
    if not os.path.exists(CLEANED_DATA_DIR):
        print(f"Cleaned data directory not found: {CLEANED_DATA_DIR}")
        return []
        
    for filename in os.listdir(CLEANED_DATA_DIR):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(CLEANED_DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split document
        md_header_splits = markdown_splitter.split_text(content)
        
        # Add Source URL to metadata
        source_url = f"https://groww.in/mutual-funds/{filename.replace('.md', '')}"
        
        for chunk in md_header_splits:
            chunk.metadata['Source URL'] = source_url
            all_chunks.append(chunk)
            
    return all_chunks

def embed_chunks(chunks):
    print(f"Total chunks created: {len(chunks)}")
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    
    # Initialize the local HuggingFace model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    texts = [chunk.page_content for chunk in chunks]
    print(f"Computing embeddings for {len(texts)} chunks...")
    
    embeddings = model.encode(texts)
    
    return embeddings

def verify_output(chunks, embeddings):
    print("\n--- Verification Output ---\n")
    for i in range(min(3, len(chunks))):
        print(f"Chunk {i+1}:")
        print(f"Metadata: {chunks[i].metadata}")
        content = chunks[i].page_content.strip()
        print(f"Content Sample: {content[:100]}...")
        print(f"Embedding Shape: {embeddings[i].shape}\n")
    
    print(f"All {len(chunks)} chunks have been successfully embedded with shape {embeddings[0].shape}.")

if __name__ == "__main__":
    chunks = load_and_chunk_documents()
    if chunks:
        embeddings = embed_chunks(chunks)
        verify_output(chunks, embeddings)
