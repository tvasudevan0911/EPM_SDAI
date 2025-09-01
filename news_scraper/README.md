# News Scraper

A Python package for scraping, storing, and searching news articles using vector similarity search.

## Project Structure

```
news_scraper/
├── data/                    # Directory for storing article JSON files
├── news_scraper/           # Main package directory
│   ├── __init__.py
│   ├── scrapers/           # News scraping modules
│   │   └── bbc_scraper.py
│   ├── db/                 # Database storage modules
│   │   └── vector_store.py
│   └── search/            # Search functionality
│       └── news_search.py
├── scripts/               # Command-line scripts
│   ├── scrape_news.py
│   ├── store_articles.py
│   └── search_articles.py
├── tests/                # Test files
├── setup.py
└── README.md
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package:
```bash
pip install -e .
```

3. Create a .env file with your Pinecone API key:
```
PINECONE_API_KEY=your-api-key-here
```

## Usage

1. Scrape latest news:
```bash
python scripts/scrape_news.py
```

2. Store articles in vector database:
```bash
python scripts/store_articles.py
```

3. Search articles:
```bash
python scripts/search_articles.py
```

## Requirements

- Python 3.8 or higher
- Pinecone account (for vector database)
- NLTK data (downloaded automatically on first run)
