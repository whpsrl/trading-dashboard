"""
AI-Powered Article Generator
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import anthropic
from groq import Groq
from ..config import settings

logger = logging.getLogger(__name__)

class ArticleGenerator:
    """Generate articles using AI from news sources"""
    
    def __init__(self):
        self.claude_client = None
        self.groq_client = None
        
        if settings.ANTHROPIC_API_KEY:
            self.claude_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        if settings.GROQ_API_KEY:
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
    
    def _build_prompt(
        self,
        articles: List[Dict],
        style: str = 'professional',
        language: str = 'en',
        max_length: int = 500
    ) -> str:
        """Build prompt for AI article generation"""
        
        # Combine article summaries
        sources_text = "\n\n".join([
            f"**{a.get('source', 'Unknown')}**: {a.get('title', '')}\n{a.get('summary', '')[:300]}"
            for a in articles[:5]  # Use top 5 articles
        ])
        
        style_guide = {
            'professional': 'professional and informative',
            'casual': 'casual and engaging',
            'technical': 'technical and detailed',
            'beginner': 'simple and easy to understand'
        }
        
        language_map = {
            'en': 'English',
            'it': 'Italian',
            'es': 'Spanish'
        }
        
        prompt = f"""You are a financial news writer. Create a compelling article based on these news sources:

{sources_text}

Requirements:
- Style: {style_guide.get(style, 'professional')}
- Language: {language_map.get(language, 'English')}
- Length: {max_length} words maximum
- Include key facts and numbers
- Add relevant emojis (but not too many)
- Structure: Headline, Summary (TL;DR), Main Content, Key Takeaways
- Cite sources at the end
- Format for Telegram (HTML or Markdown)

Write the article now:"""
        
        return prompt
    
    async def generate_with_claude(
        self,
        articles: List[Dict],
        style: str = 'professional',
        language: str = 'en',
        max_length: int = 500
    ) -> Optional[str]:
        """Generate article using Claude"""
        if not self.claude_client:
            logger.error("Claude API not configured")
            return None
        
        try:
            prompt = self._build_prompt(articles, style, language, max_length)
            
            # Synchronous call (Claude SDK doesn't require async)
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            article = response.content[0].text
            return article
            
        except Exception as e:
            logger.error(f"Error generating article with Claude: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate_with_groq(
        self,
        articles: List[Dict],
        style: str = 'professional',
        language: str = 'en',
        max_length: int = 500
    ) -> Optional[str]:
        """Generate article using Groq"""
        if not self.groq_client:
            logger.error("Groq API not configured")
            return None
        
        try:
            prompt = self._build_prompt(articles, style, language, max_length)
            
            # Synchronous call
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )
            
            article = response.choices[0].message.content
            return article
            
        except Exception as e:
            logger.error(f"Error generating article with Groq: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate(
        self,
        articles: List[Dict],
        ai_provider: str = 'claude',
        style: str = 'professional',
        language: str = 'en',
        max_length: int = 500
    ) -> Optional[Dict]:
        """Generate article with specified AI provider"""
        
        if not articles:
            logger.error("No articles provided")
            return None
        
        logger.info(f"🤖 Generating article with {ai_provider.upper()} from {len(articles)} sources...")
        
        # Generate article
        if ai_provider == 'claude':
            content = await self.generate_with_claude(articles, style, language, max_length)
        elif ai_provider == 'groq':
            content = await self.generate_with_groq(articles, style, language, max_length)
        else:
            logger.error(f"Unknown AI provider: {ai_provider}")
            return None
        
        if not content:
            return None
        
        # Extract sources
        sources = [
            {'title': a.get('title'), 'link': a.get('link'), 'source': a.get('source')}
            for a in articles[:5]
        ]
        
        result = {
            'content': content,
            'sources': sources,
            'ai_provider': ai_provider,
            'style': style,
            'language': language,
            'generated_at': datetime.utcnow().isoformat(),
            'word_count': len(content.split())
        }
        
        logger.info(f"✅ Article generated: {result['word_count']} words")
        
        return result
    
    def format_for_telegram(self, article: Dict) -> str:
        """Format article for Telegram with HTML"""
        content = article.get('content', '')
        sources = article.get('sources', [])
        
        # Add sources footer
        sources_text = "\n\n📚 <b>Sources:</b>\n"
        for src in sources:
            sources_text += f"• <a href='{src['link']}'>{src['source']}</a>\n"
        
        # Add metadata
        footer = f"\n\n🤖 Generated with {article.get('ai_provider', 'AI').upper()}"
        footer += f"\n⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')} CET"
        
        return content + sources_text + footer


# Global instance
article_generator = ArticleGenerator()

