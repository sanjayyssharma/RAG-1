import sys
import os

# Add the project root to sys.path so we can import modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from src.phase1_ingestion.phase1_1_scraping.scraper import scrape_and_save
from src.phase1_ingestion.phase1_2_cleaning.cleaner import run_cleaner
from src.phase1_ingestion.phase1_4_vectordb.vector_store import populate_database

def run_update_pipeline():
    print("="*50)
    print("🚀 Starting Automated Corpus Update Pipeline")
    print("="*50)
    
    # Step 1: Scrape new data
    print("\n[Step 1/3] Scraping fresh mutual fund data from Groww...")
    scrape_and_save()
    
    # Step 2: Clean and format data
    print("\n[Step 2/3] Cleaning HTML noise and standardizing Markdown...")
    run_cleaner()
    
    # Step 3: Chunk and Vectorize into ChromaDB
    print("\n[Step 3/3] Chunking, computing embeddings, and updating Vector DB...")
    # This will automatically delete the old collection and create a new one
    collection = populate_database()
    
    if collection:
        print("\n✅ Pipeline completed successfully. The Mutual Fund database is up-to-date!")
    else:
        print("\n❌ Pipeline failed during vectorization.")
        sys.exit(1)

if __name__ == "__main__":
    run_update_pipeline()
