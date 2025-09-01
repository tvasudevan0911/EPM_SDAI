"""
BBC News scraper module
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from urllib.parse import urljoin
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from collections import Counter
from string import punctuation

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')
    nltk.download('tagsets')
except Exception as e:
    print(f"Warning: Could not download NLTK data: {str(e)}")

class NewsScraperError(Exception):
    """Custom exception for news scraper errors"""
    pass

class NewsScraper:
    def __init__(self, base_url, delay=1):
        self.base_url = base_url
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            self.stop_words = set(stopwords.words('english'))
            self.stop_words.update(['said', 'says', 'would', 'could', 'also', 'like', 'one', 'two', 'first', 'last', 'year', 'years'])
        except Exception as e:
            print(f"Warning: Could not load stopwords: {str(e)}")
            self.stop_words = set()

    def get_soup(self, url):
        """Make request and return BeautifulSoup object"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            raise NewsScraperError(f"Failed to fetch URL: {url}. Error: {str(e)}")

    def extract_keywords_simple(self, text, title):
        """Extract keywords using a simpler approach"""
        try:
            full_text = f"{title} {text}"
            words = re.findall(r'\b\w+\b', full_text.lower())
            words = [word for word in words 
                    if word not in self.stop_words 
                    and len(word) > 3]
            word_freq = Counter(words)
            top_keywords = [word for word, _ in word_freq.most_common(8)]
            return top_keywords
        except Exception as e:
            print(f"Warning: Could not extract keywords: {str(e)}")
            return []

    def extract_article(self, url):
        """Extract article content from URL"""
        try:
            soup = self.get_soup(url)
            
            title_elem = soup.find('h1')
            heading = title_elem.get_text().strip() if title_elem else "No heading found"

            article_body = soup.find('article') or soup.find('main')
            content = ""
            
            if article_body:
                text_blocks = article_body.find_all(['div', 'p'])
                content = ' '.join(block.get_text().strip() for block in text_blocks if block.get_text().strip())
            else:
                paragraphs = soup.find_all('p')
                content = ' '.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

            keywords = self.extract_keywords_simple(content, heading)

            article = {
                'url': url,
                'heading': heading,
                'content': content,
                'keywords': keywords,
                'source': 'BBC News',
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }

            print(f"Scraped: {heading} from BBC News")
            return article

        except Exception as e:
            print(f"Error scraping article {url}: {str(e)}")
            return None

    def scrape_latest_news(self, limit=10):
        """Scrape latest news articles from BBC News"""
        try:
            articles = []
            seen_urls = set()
            soup = self.get_soup(self.base_url)
            
            for link in soup.find_all('a', href=True):
                if len(articles) >= limit:
                    break
                    
                href = link.get('href', '')
                if '/news/articles/' in href:
                    full_url = urljoin(self.base_url, href)
                    
                    if full_url in seen_urls:
                        continue
                        
                    seen_urls.add(full_url)
                    article = self.extract_article(full_url)
                    if article:
                        articles.append(article)

            return articles

        except Exception as e:
            raise NewsScraperError(f"Failed to scrape latest news. Error: {str(e)}")

def save_articles(articles, output_dir='data'):
    """Save articles to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'news_articles_{timestamp}.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    
    return output_file
