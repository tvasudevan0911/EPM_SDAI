"""
Search module for finding relevant news articles
"""
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class NewsSearch:
    def __init__(self, api_key: str, index_name: str = "news-articles-index"):
        """Initialize the search engine with Pinecone and BERT model"""
        if not api_key:
            raise ValueError("Pinecone API key is required")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.index = self.pc.Index(self.index_name)
        
        # Initialize the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def preprocess_query(self, query: str) -> List[str]:
        """Preprocess the query into relevant terms"""
        terms = query.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        terms = [term for term in terms if term not in stop_words]
        return terms

    def search(self, query: str, top_k: int = 5, min_score: float = 0.15) -> List[Dict]:
        """
        Search for articles similar to the query
        """
        # Preprocess query
        search_terms = self.preprocess_query(query)
        
        # Generate embedding for the query
        query_embedding = self.model.encode(query)
        
        # Debug: Print raw results
        print("\nDebug - Raw results:")
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=top_k * 3,  # Get more results for filtering
            include_metadata=True
        )
        
        for match in results['matches']:
            print(f"Score: {match['score']:.3f}, Title: {match['metadata']['heading']}")
        
        # Format results with additional relevance scoring
        seen_urls = set()
        articles = []
        
        for match in results['matches']:
            url = match['metadata']['url']
            
            if url in seen_urls:
                continue
            
            # Calculate text match score based on search terms
            text_content = f"{match['metadata']['heading']} {match['metadata'].get('content_preview', '')}".lower()
            term_matches = sum(1 for term in search_terms if term in text_content)
            text_match_boost = min(term_matches * 0.15, 0.45)  # Cap boost at 0.45
            
            # Combine semantic similarity with text match score
            combined_score = match['score'] + text_match_boost
            
            if combined_score < min_score:
                continue
                
            seen_urls.add(url)
            article = {
                'score': combined_score,
                'url': url,
                'heading': match['metadata']['heading'],
                'summary': match['metadata'].get('summary', 'No summary available'),
                'source': match['metadata']['source']
            }
            articles.append(article)
            
            if len(articles) >= top_k:
                break
                
        # Sort by combined score
        articles.sort(key=lambda x: x['score'], reverse=True)
        return articles

    def print_results(self, results: List[Dict]):
        """Pretty print search results"""
        # Remove duplicates based on URL while preserving order
        seen_urls = set()
        unique_results = []
        for article in results:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_results.append(article)
        
        print(f"\nFound {len(unique_results)} unique matching articles:")
        print("=" * 80)
        
        for i, article in enumerate(unique_results, 1):
            print(f"\n{i}. {article['heading']}")
            print(f"Relevance Score: {article['score']:.3f}")
            print(f"Source: {article['source']}")
            print(f"URL: {article['url']}")
            print(f"\nSummary: {article['summary']}")
            print("-" * 80)
