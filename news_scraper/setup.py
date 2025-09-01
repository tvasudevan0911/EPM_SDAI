from setuptools import setup, find_packages

setup(
    name="news_scraper",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'requests',
        'pinecone-client',
        'sentence-transformers',
        'transformers[torch]',
        'nltk',
        'python-dotenv'
    ],
    python_requires='>=3.8',
    scripts=[
        'scripts/scrape_news.py',
        'scripts/store_articles.py',
        'scripts/search_articles.py'
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for scraping, storing, and searching news articles",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/news_scraper",
)
