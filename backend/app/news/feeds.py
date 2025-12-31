"""
RSS Feed Scraper for Financial News
"""
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsFeedScraper:
    """Scrape news from RSS feeds"""
    
    # RSS Feed URLs
    FEEDS = {
        # CRYPTO
        'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'cointelegraph': 'https://cointelegraph.com/rss',
        'decrypt': 'https://decrypt.co/feed',
        'theblock': 'https://www.theblock.co/rss.xml',
        'bitcoinmagazine': 'https://bitcoinmagazine.com/.rss/full/',
        
        # FINANCE
        'reuters_markets': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'seekingalpha': 'https://seekingalpha.com/market_currents.xml',
        'investing': 'https://www.investing.com/rss/news.rss',
        'benzinga': 'https://www.benzinga.com/feed',
        
        # TECH
        'techcrunch': 'https://techcrunch.com/feed/',
        'theverge': 'https://www.theverge.com/rss/index.xml',
        'arstechnica': 'https://feeds.arstechnica.com/arstechnica/index',
        'venturebeat': 'https://venturebeat.com/feed/',
        
        # ITALIAN
        'sole24ore': 'https://www.ilsole24ore.com/rss/finanza-e-mercati.xml',
        'milanofinanza': 'https://www.milanofinanza.it/rss',
        'cryptonomist': 'https://en.cryptonomist.ch/feed/',
    }
    
    CATEGORIES = {
        'crypto': ['coindesk', 'cointelegraph', 'decrypt', 'theblock', 'bitcoinmagazine', 'cryptonomist'],
        'finance': ['reuters_markets', 'seekingalpha', 'investing', 'benzinga', 'sole24ore', 'milanofinanza'],
        'tech': ['techcrunch', 'theverge', 'arstechnica', 'venturebeat'],
    }
    
    def __init__(self):
        self.session = None
    
    async def fetch_feed(self, feed_url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:10]:  # Get latest 10
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'published_parsed': entry.get('published_parsed', None),
                    'source': feed.feed.get('title', 'Unknown'),
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            return []
    
    async def fetch_category(self, category: str, max_articles: int = 20) -> List[Dict]:
        """Fetch articles from a category"""
        if category not in self.CATEGORIES:
            logger.error(f"Unknown category: {category}")
            return []
        
        feed_names = self.CATEGORIES[category]
        all_articles = []
        
        for feed_name in feed_names:
            if feed_name not in self.FEEDS:
                continue
            
            feed_url = self.FEEDS[feed_name]
            articles = await self.fetch_feed(feed_url)
            
            for article in articles:
                article['category'] = category
                article['feed_name'] = feed_name
            
            all_articles.extend(articles)
        
        # Sort by published date
        all_articles.sort(
            key=lambda x: x.get('published_parsed', datetime.now().timetuple()),
            reverse=True
        )
        
        return all_articles[:max_articles]
    
    async def fetch_all(self, hours_ago: int = 24) -> Dict[str, List[Dict]]:
        """Fetch all feeds, grouped by category"""
        cutoff_time = datetime.now() - timedelta(hours=hours_ago)
        
        result = {}
        for category in self.CATEGORIES.keys():
            articles = await self.fetch_category(category)
            
            # Filter by time
            recent_articles = []
            for article in articles:
                pub_time = article.get('published_parsed')
                if pub_time:
                    article_time = datetime(*pub_time[:6])
                    if article_time >= cutoff_time:
                        recent_articles.append(article)
                else:
                    recent_articles.append(article)  # Include if no date
            
            result[category] = recent_articles
        
        return result
    
    async def search_topic(self, keyword: str, category: Optional[str] = None) -> List[Dict]:
        """Search articles by keyword"""
        if category:
            articles = await self.fetch_category(category)
        else:
            all_feeds = await self.fetch_all(hours_ago=48)
            articles = []
            for cat_articles in all_feeds.values():
                articles.extend(cat_articles)
        
        # Filter by keyword
        keyword_lower = keyword.lower()
        matching = [
            a for a in articles
            if keyword_lower in a.get('title', '').lower() 
            or keyword_lower in a.get('summary', '').lower()
        ]
        
        return matching
    
    def get_feed_list(self) -> Dict[str, List[str]]:
        """Get available feeds by category"""
        return {
            'categories': list(self.CATEGORIES.keys()),
            'feeds': self.FEEDS,
            'by_category': self.CATEGORIES
        }


# Global instance
news_scraper = NewsFeedScraper()

