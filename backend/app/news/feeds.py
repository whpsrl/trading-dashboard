"""
RSS Feed Scraper for Financial News
"""
import feedparser
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta

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
        'crypto': ['coindesk', 'cointelegraph', 'decrypt', 'theblock', 'bitcoinmagazine'],
        'finance': ['reuters_markets', 'seekingalpha', 'investing', 'benzinga', 'sole24ore'],
        'tech': ['techcrunch', 'theverge', 'arstechnica', 'venturebeat'],
    }
    
    def __init__(self):
        self.session = None
    
    async def fetch_feed(self, feed_url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            logger.info(f"📡 Fetching RSS feed: {feed_url}")
            
            # Run feedparser in thread pool (it's blocking/synchronous)
            feed = await asyncio.to_thread(feedparser.parse, feed_url)
            
            if not feed:
                logger.warning(f"⚠️ Empty response from {feed_url}")
                return []
            
            # Check if feed has entries
            if not hasattr(feed, 'entries'):
                logger.warning(f"⚠️ No 'entries' attribute in feed from {feed_url}")
                return []
            
            if not feed.entries:
                logger.warning(f"⚠️ Feed has 0 entries from {feed_url}")
                return []
            
            # Get feed title safely
            feed_title = 'Unknown Source'
            if hasattr(feed, 'feed'):
                feed_title = feed.feed.get('title', 'Unknown Source')
            
            logger.info(f"✅ Found {len(feed.entries)} entries in {feed_title}")
            
            articles = []
            for entry in feed.entries[:10]:  # Get latest 10
                # Extract data with fallbacks
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                published = entry.get('published', '')
                published_parsed = entry.get('published_parsed', None)
                
                # Only add if has at least a title
                if title:
                    article = {
                        'title': title,
                        'link': link,
                        'summary': summary,
                        'published': published,
                        'published_parsed': published_parsed,
                        'source': feed_title,
                    }
                    articles.append(article)
            
            logger.info(f"✅ Extracted {len(articles)} valid articles from {feed_title}")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching feed {feed_url}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def fetch_category(self, category: str, max_articles: int = 20) -> List[Dict]:
        """Fetch articles from a category"""
        logger.info(f"📰 Fetching news for category: {category}")
        
        if category not in self.CATEGORIES:
            logger.error(f"❌ Unknown category: {category}")
            return []
        
        feed_names = self.CATEGORIES[category]
        all_articles = []
        
        # Fetch from all feeds in category
        for feed_name in feed_names:
            if feed_name not in self.FEEDS:
                logger.warning(f"⚠️ Feed {feed_name} not found in FEEDS dict")
                continue
            
            feed_url = self.FEEDS[feed_name]
            logger.info(f"   📡 Fetching from {feed_name}...")
            
            articles = await self.fetch_feed(feed_url)
            
            # Add metadata
            for article in articles:
                article['category'] = category
                article['feed_name'] = feed_name
            
            all_articles.extend(articles)
            logger.info(f"   ✅ Got {len(articles)} articles from {feed_name}")
        
        logger.info(f"✅ Total articles fetched: {len(all_articles)}")
        
        # Sort by published date (most recent first)
        try:
            all_articles.sort(
                key=lambda x: x.get('published_parsed') or datetime.now().timetuple(),
                reverse=True
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not sort articles: {e}")
        
        # Return max_articles
        result = all_articles[:max_articles]
        logger.info(f"📋 Returning {len(result)} articles (max: {max_articles})")
        
        return result
    
    async def fetch_all(self, hours_ago: int = 24) -> Dict[str, List[Dict]]:
        """Fetch all feeds, grouped by category"""
        cutoff_time = datetime.now() - timedelta(hours=hours_ago)
        
        result = {}
        for category in self.CATEGORIES.keys():
            logger.info(f"📰 Fetching category: {category}")
            articles = await self.fetch_category(category)
            
            # Filter by time if published_parsed exists
            recent_articles = []
            for article in articles:
                pub_time = article.get('published_parsed')
                if pub_time:
                    try:
                        article_time = datetime(*pub_time[:6])
                        if article_time >= cutoff_time:
                            recent_articles.append(article)
                    except:
                        # If date parsing fails, include it anyway
                        recent_articles.append(article)
                else:
                    # No date, include it
                    recent_articles.append(article)
            
            result[category] = recent_articles
            logger.info(f"   ✅ {category}: {len(recent_articles)} recent articles")
        
        return result
    
    async def search_topic(self, keyword: str, category: Optional[str] = None) -> List[Dict]:
        """Search articles by keyword"""
        logger.info(f"🔍 Searching for keyword: '{keyword}' in category: {category or 'all'}")
        
        if category:
            articles = await self.fetch_category(category)
        else:
            all_feeds = await self.fetch_all(hours_ago=48)
            articles = []
            for cat_articles in all_feeds.values():
                articles.extend(cat_articles)
        
        # Filter by keyword (case insensitive)
        keyword_lower = keyword.lower()
        matching = [
            a for a in articles
            if keyword_lower in a.get('title', '').lower() 
            or keyword_lower in a.get('summary', '').lower()
        ]
        
        logger.info(f"✅ Found {len(matching)} articles matching '{keyword}'")
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

