#!/usr/bin/env python3
"""
Script to store articles in vector database
"""
import os
from dotenv import load_dotenv
from news_scraper.db.vector_store import VectorDBStorage

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Pinecone API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    
    # Initialize vector store
    store = VectorDBStorage(api_key)
    
    # Find the latest articles file
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    articles_files = [f for f in os.listdir(data_dir) if f.startswith('news_articles_') and f.endswith('.json')]
    
    if not articles_files:
        print("No article files found in data directory")
        return
    
    # Get the most recent file
    latest_file = sorted(articles_files)[-1]
    articles_file = os.path.join(data_dir, latest_file)
    
    # Store articles in vector database
    store.store_articles(articles_file)

if __name__ == "__main__":
    main()
