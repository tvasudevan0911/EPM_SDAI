"""
Vector database storage module using Pinecone
"""
import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from typing import List, Dict
import json

# Initialize models
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=150)

class VectorDBStorage:
    def __init__(self, api_key: str, index_name: str = "news-articles-index", environment: str = "us-west1-gcp"):
        """Initialize Pinecone client with API key"""
        self.api_key = api_key
        self.environment = environment
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        
    def get_index(self, index_name: str):
        """Get or create Pinecone index"""
        try:
            existing_indexes = self.pc.list_indexes()
            
            if index_name not in [index.name for index in existing_indexes]:
                print(f"Creating new index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=384,  # all-MiniLM-L6-v2 produces 384-dimensional embeddings
                    metric='cosine',
                    spec=ServerlessSpec(cloud="aws", region="us-west-2")
                )
            else:
                print(f"Using existing index: {index_name}")
                
            return self.pc.Index(name=index_name)
        except Exception as e:
            print(f"Error with Pinecone index: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = embedding_model.encode(text)
        return [float(x) for x in embedding]

    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate a concise summary of the article"""
        try:
            paragraphs = text.split('\n\n')[:3]
            text_to_summarize = ' '.join(paragraphs)
            words = text_to_summarize.split()[:1000]
            truncated_text = ' '.join(words)
            
            summary = summarizer(truncated_text, 
                              max_length=max_length, 
                              min_length=30, 
                              do_sample=False,
                              truncation=True)[0]['summary_text']
            return summary.strip()
        except Exception as e:
            print(f"Warning: Could not generate summary: {str(e)}")
            return text.split('\n\n')[0] if text else ""

    def prepare_article_vector(self, article: Dict) -> Dict:
        """Prepare article data for vector database storage"""
        summary = self.generate_summary(article['content'])
        
        # Combine title and first few paragraphs for embedding
        paragraphs = article['content'].split('\n\n')[:3]
        content_for_embedding = f"{article['heading']} {' '.join(paragraphs)}"
        embedding = self.generate_embedding(content_for_embedding)
        
        # Create unique ID
        unique_id = str(abs(hash(article['url'])))[:12]
        
        # Create truncated metadata to stay under Pinecone's 40KB limit
        metadata = {
            'url': article['url'][:500],  # Limit URL length
            'heading': article['heading'][:200],  # Limit heading length
            'summary': summary[:1000],  # Limit summary length
            'keywords': article['keywords'][:500],  # Limit keywords length
            'source': article['source'][:100],  # Limit source length
            'scraped_at': article['timestamp'],
            'content_preview': ' '.join(paragraphs[:1])[:2000]  # Limit preview length and use only first paragraph
        }
        
        return {
            'id': unique_id,
            'values': embedding,
            'metadata': metadata
        }

    def store_articles(self, articles_file: str) -> None:
        """Store articles from JSON file in vector database"""
        print(f"Loading articles from: {articles_file}\n")
        with open(articles_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"Storing articles in index: {self.index_name}")
        index = self.get_index(self.index_name)
        
        # Get existing articles to check for duplicates
        existing_count = 0
        try:
            stats = index.describe_index_stats()
            existing_count = stats.total_vector_count
        except Exception as e:
            print(f"Could not get index stats: {str(e)}")
        
        print(f"Found {existing_count} existing articles in the index")
        
        # Prepare vectors for all articles
        vectors = []
        urls_seen = set()
        skipped = 0
        
        for article in articles:
            if article['url'] in urls_seen:
                skipped += 1
                continue
            
            urls_seen.add(article['url'])
            vector = self.prepare_article_vector(article)
            vectors.append(vector)
        
        print(f"Skipped {skipped} duplicate articles")
        
        # Store vectors in batches
        if vectors:
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                try:
                    index.upsert(vectors=batch)
                    print(f"Stored batch of {len(batch)} articles")
                except Exception as e:
                    print(f"Error storing batch: {str(e)}")
                    raise
        else:
            print("No new articles to store")
        
        print("Articles stored successfully!")
        print("You can now query these articles using vector similarity search!")
