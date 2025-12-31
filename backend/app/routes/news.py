"""
News/Articles API Routes
"""
import logging
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Optional
from ..news.feeds import news_scraper
from ..news.article_generator import article_generator
from ..database.tracker import trade_tracker
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


def get_telegram():
    """Get telegram instance from main module"""
    try:
        from .. import main
        return main.telegram
    except:
        return None


@router.get("/feeds")
async def get_available_feeds():
    """Get list of available RSS feeds by category"""
    try:
        feeds_info = news_scraper.get_feed_list()
        return {
            "success": True,
            "data": feeds_info
        }
    except Exception as e:
        logger.error(f"❌ Error getting feeds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch")
async def fetch_news(
    category: Optional[str] = Query(None, description="Category: crypto, finance, tech"),
    hours_ago: int = Query(24, description="Fetch news from last N hours"),
    max_articles: int = Query(20, description="Max articles to fetch")
):
    """Fetch news from RSS feeds"""
    try:
        if category:
            articles = await news_scraper.fetch_category(category, max_articles)
            return {
                "success": True,
                "category": category,
                "count": len(articles),
                "articles": articles
            }
        else:
            all_articles = await news_scraper.fetch_all(hours_ago)
            total_count = sum(len(arts) for arts in all_articles.values())
            return {
                "success": True,
                "count": total_count,
                "by_category": all_articles
            }
    except Exception as e:
        logger.error(f"❌ Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_news(
    keyword: str = Query(..., description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Search news articles by keyword"""
    try:
        articles = await news_scraper.search_topic(keyword, category)
        return {
            "success": True,
            "keyword": keyword,
            "category": category,
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        logger.error(f"❌ Error searching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_article(
    category: str = Query(..., description="Category: crypto, finance, tech"),
    ai_provider: str = Query("claude", pattern="^(claude|groq)$"),
    style: str = Query("professional", description="Style: professional, casual, technical, beginner"),
    language: str = Query("en", description="Language: en, it"),
    max_length: int = Query(500, description="Max word count"),
    keyword: Optional[str] = Query(None, description="Optional keyword filter"),
    save_to_db: bool = Query(True, description="Save article to database")
):
    """Generate AI article from recent news"""
    try:
        logger.info(f"📰 Generating {language} article about {category} with {ai_provider.upper()}...")
        
        # Fetch recent news
        logger.info(f"📡 Fetching news for category: {category}, keyword: {keyword}")
        if keyword:
            articles = await news_scraper.search_topic(keyword, category)
        else:
            articles = await news_scraper.fetch_category(category, max_articles=10)
        
        logger.info(f"✅ Fetched {len(articles)} articles")
        
        if not articles:
            logger.warning(f"⚠️ No articles found for category '{category}'")
            return {
                "success": False,
                "error": f"No recent articles found for category '{category}'"
            }
        
        # Generate article with AI
        logger.info(f"🤖 Generating article with {ai_provider}...")
        result = await article_generator.generate(
            articles=articles,
            ai_provider=ai_provider,
            style=style,
            language=language,
            max_length=max_length
        )
        
        if not result:
            logger.error("❌ AI generation returned None")
            return {
                "success": False,
                "error": "Failed to generate article with AI. Check API keys and rate limits."
            }
        
        logger.info(f"✅ Article generated: {result.get('word_count', 0)} words")
        
        # Format for Telegram
        telegram_content = article_generator.format_for_telegram(result)
        
        # Save to database if requested
        article_id = None
        if save_to_db:
            from ..database.tracker import SessionLocal
            from ..database.models import NewsArticle
            
            db = SessionLocal()
            try:
                # Extract title from content (first line usually)
                content_lines = result['content'].split('\n')
                title = content_lines[0].replace('#', '').strip() if content_lines else "Untitled"
                
                article = NewsArticle(
                    title=title,
                    content=result['content'],
                    summary=None,  # Could extract TL;DR section
                    category=category,
                    language=language,
                    style=style,
                    word_count=result['word_count'],
                    ai_provider=ai_provider,
                    sources=result['sources'],
                    status='draft'
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                article_id = article.id
                logger.info(f"✅ Article saved to database with ID: {article_id}")
            except Exception as e:
                logger.error(f"❌ Error saving article to DB: {e}")
                import traceback
                traceback.print_exc()
                db.rollback()
            finally:
                db.close()
        
        return {
            "success": True,
            "article": result,
            "telegram_formatted": telegram_content,
            "article_id": article_id,
            "source_count": len(articles)
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating article: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles")
async def get_articles(
    status: Optional[str] = Query(None, description="Filter by status: draft, published, archived"),
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    limit: int = Query(50, description="Max results"),
    offset: int = Query(0, description="Skip N results")
):
    """Get articles from database"""
    from ..database.tracker import SessionLocal
    from ..database.models import NewsArticle
    
    db = SessionLocal()
    try:
        query = db.query(NewsArticle)
        
        if status:
            query = query.filter(NewsArticle.status == status)
        if category:
            query = query.filter(NewsArticle.category == category)
        if language:
            query = query.filter(NewsArticle.language == language)
        
        articles = query.order_by(NewsArticle.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "count": len(articles),
            "articles": [a.to_dict() for a in articles]
        }
    except Exception as e:
        logger.error(f"❌ Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/publish/{article_id}")
async def publish_article(
    article_id: int,
    topic: str = Query("news_articles", description="Telegram topic: news_articles, education, general")
):
    """Publish article to Telegram"""
    from ..database.tracker import SessionLocal
    from ..database.models import NewsArticle
    
    telegram = get_telegram()
    
    if not telegram or not telegram.is_available():
        raise HTTPException(status_code=503, detail="Telegram not available")
    
    db = SessionLocal()
    try:
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Format for Telegram
        article_dict = article.to_dict()
        telegram_content = article_generator.format_for_telegram(article_dict)
        
        # Send to Telegram
        result = await telegram.send_article(
            {'content': telegram_content},
            topic=topic
        )
        
        if result['success']:
            # Update article status
            article.status = 'published'
            article.published_at = datetime.utcnow()
            article.telegram_message_id = result.get('message_id')
            article.telegram_topic_id = result.get('topic_id')
            db.commit()
            
            logger.info(f"✅ Article {article_id} published to Telegram")
            
            return {
                "success": True,
                "message": "Article published successfully",
                "telegram_message_id": result.get('message_id'),
                "article": article.to_dict()
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Unknown error')
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error publishing article: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/articles/{article_id}")
async def delete_article(article_id: int):
    """Delete an article"""
    from ..database.tracker import SessionLocal
    from ..database.models import NewsArticle
    
    db = SessionLocal()
    try:
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        db.delete(article)
        db.commit()
        
        return {
            "success": True,
            "message": f"Article {article_id} deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting article: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

