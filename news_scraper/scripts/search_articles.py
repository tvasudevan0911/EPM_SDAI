#!/usr/bin/env python3
"""
Script to search articles in vector database
"""
import os
from dotenv import load_dotenv
from news_scraper.search.news_search import NewsSearch

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Pinecone API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    
    # Initialize search engine
    search_engine = NewsSearch(api_key)
    
    while True:
        # Get search query
        query = input("\nEnter your search query (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            print("Please enter a search query")
            continue
        
        try:
            # Perform search
            results = search_engine.search(query)
            
            # Print results
            search_engine.print_results(results)
            
        except Exception as e:
            print(f"Error during search: {str(e)}")

if __name__ == "__main__":
    main()
