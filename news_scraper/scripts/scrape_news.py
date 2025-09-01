#!/usr/bin/env python3
"""
Script to scrape latest news articles
"""
import os
from dotenv import load_dotenv
from news_scraper.scrapers.bbc_scraper import NewsScraper, save_articles

def main():
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize scraper with BBC News URL
    scraper = NewsScraper('https://www.bbc.com/news')
    
    try:
        print("Fetching latest news articles...")
        
        # Scrape latest articles
        articles = scraper.scrape_latest_news(limit=10)
        
        # Save articles to JSON file
        output_file = save_articles(articles, data_dir)
        
        print(f"\nArticles saved to {output_file} \n")
        print(f"Scraped {len(articles)} articles:\n")
        
        # Print article details
        for article in articles:
            print(f"Heading: {article['heading']}")
            print(f"Source: {article['source']}")
            print(f"Keywords: {', '.join(article['keywords'])}")
            print(f"URL: {article['url']}")
            print("-" * 50 + "\n")
            
        print("Scraping completed.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
