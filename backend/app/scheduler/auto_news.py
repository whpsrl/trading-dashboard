"""
Auto News Article Scheduler
Generates and posts articles automatically to Telegram Topics
"""
import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import UTC

from ..news.feeds import news_scraper
from ..news.article_generator import article_generator
from ..telegram.bot import TelegramNotifier
from ..database.tracker import SessionLocal
from ..database.models import NewsArticle

logger = logging.getLogger(__name__)


class AutoNewsScheduler:
    """Schedule automatic article generation and posting"""
    
    def __init__(self, telegram: TelegramNotifier):
        self.telegram = telegram
        self.scheduler = AsyncIOScheduler(timezone=UTC)
        
        # Configuration
        self.categories = ['crypto', 'finance', 'tech']
        self.default_style = 'professional'
        self.default_language = 'en'
        self.ai_provider = 'claude'  # Default AI
        
        logger.info("✅ Auto News Scheduler initialized")
    
    async def generate_and_post_article(self, category: str):
        """Generate article for a category and post to Telegram"""
        try:
            logger.info(f"📰 Auto-generating {category} article...")
            
            # Fetch recent news
            articles = await news_scraper.fetch_category(category, max_articles=10)
            
            if not articles:
                logger.warning(f"⚠️ No articles found for {category}")
                return
            
            # Generate article with AI
            result = await article_generator.generate(
                articles=articles,
                ai_provider=self.ai_provider,
                style=self.default_style,
                language=self.default_language,
                max_length=500
            )
            
            if not result:
                logger.error(f"❌ Failed to generate article for {category}")
                return
            
            # Save to database
            db = SessionLocal()
            try:
                content_lines = result['content'].split('\n')
                title = content_lines[0].replace('#', '').strip() if content_lines else f"{category.capitalize()} Update"
                
                article = NewsArticle(
                    title=title,
                    content=result['content'],
                    category=category,
                    language=self.default_language,
                    style=self.default_style,
                    word_count=result['word_count'],
                    ai_provider=self.ai_provider,
                    sources=result['sources'],
                    status='published'  # Mark as published since we'll post it immediately
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                
                logger.info(f"✅ Article saved with ID: {article.id}")
                
                # Format for Telegram
                telegram_content = article_generator.format_for_telegram(result)
                
                # Post to Telegram (news_articles topic)
                if self.telegram and self.telegram.is_available():
                    post_result = await self.telegram.send_article(
                        {'content': telegram_content},
                        topic='news_articles'
                    )
                    
                    if post_result['success']:
                        # Update article with Telegram info
                        article.published_at = datetime.utcnow()
                        article.telegram_message_id = post_result.get('message_id')
                        article.telegram_topic_id = post_result.get('topic_id')
                        db.commit()
                        
                        logger.info(f"✅ Article posted to Telegram! Message ID: {post_result.get('message_id')}")
                    else:
                        logger.error(f"❌ Failed to post to Telegram: {post_result.get('error')}")
                else:
                    logger.warning("⚠️ Telegram not available, article saved but not posted")
                
            except Exception as e:
                logger.error(f"❌ Error saving/posting article: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error in auto article generation: {e}")
    
    async def run_morning_crypto_news(self):
        """Morning crypto news (8:00 UTC = 9:00 CET)"""
        logger.info("☀️ Running morning crypto news...")
        await self.generate_and_post_article('crypto')
    
    async def run_afternoon_finance_news(self):
        """Afternoon finance news (14:00 UTC = 15:00 CET)"""
        logger.info("📊 Running afternoon finance news...")
        await self.generate_and_post_article('finance')
    
    async def run_evening_tech_news(self):
        """Evening tech news (18:00 UTC = 19:00 CET)"""
        logger.info("💻 Running evening tech news...")
        await self.generate_and_post_article('tech')
    
    def start(self):
        """Start the scheduler"""
        # Morning crypto news - 8:00 UTC (9:00 Rome)
        self.scheduler.add_job(
            self.run_morning_crypto_news,
            CronTrigger(hour=8, minute=0),
            id='morning_crypto_news',
            name='Morning Crypto News (8:00 UTC)',
            replace_existing=True
        )
        
        # Afternoon finance news - 14:00 UTC (15:00 Rome)
        self.scheduler.add_job(
            self.run_afternoon_finance_news,
            CronTrigger(hour=14, minute=0),
            id='afternoon_finance_news',
            name='Afternoon Finance News (14:00 UTC)',
            replace_existing=True
        )
        
        # Evening tech news - 18:00 UTC (19:00 Rome)
        self.scheduler.add_job(
            self.run_evening_tech_news,
            CronTrigger(hour=18, minute=0),
            id='evening_tech_news',
            name='Evening Tech News (18:00 UTC)',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("✅ Auto News Scheduler started:")
        logger.info("   📰 Morning Crypto: 08:00 UTC (09:00 Rome)")
        logger.info("   📰 Afternoon Finance: 14:00 UTC (15:00 Rome)")
        logger.info("   📰 Evening Tech: 18:00 UTC (19:00 Rome)")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("👋 Auto News Scheduler stopped")

