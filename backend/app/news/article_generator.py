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
        
        # Combine article summaries with more detail
        sources_text = ""
        for idx, article in enumerate(articles[:5], 1):  # Use top 5 articles
            sources_text += f"\n\n=== FONTE {idx}: {article.get('source', 'Unknown')} ===\n"
            sources_text += f"Titolo: {article.get('title', 'N/A')}\n"
            if article.get('summary'):
                sources_text += f"Contenuto: {article.get('summary', '')[:500]}\n"
            if article.get('link'):
                sources_text += f"Link: {article.get('link')}\n"
        
        style_guide = {
            'professional': 'professionale e informativo, adatto a trader e investitori esperti',
            'casual': 'casual e coinvolgente, accessibile a tutti',
            'technical': 'tecnico e dettagliato, con analisi approfondite',
            'beginner': 'semplice e comprensibile, ideale per principianti'
        }
        
        language_map = {
            'en': 'English',
            'it': 'Italian',
            'es': 'Spanish'
        }
        
        language_instructions = {
            'en': '',
            'it': '\n- Usa italiano professionale e corretto\n- Termini tecnici in inglese solo se necessari (con spiegazione)',
            'es': '\n- Usa español profesional y correcto'
        }
        
        prompt = f"""Sei un giornalista esperto di finanza e trading. Ho raccolto informazioni da {len(articles)} fonti autorevoli.

CONTENUTI DALLE FONTI:
{sources_text}

Il tuo compito è creare un articolo ORIGINALE che:

1. **Analizza e sintetizza** le informazioni dalle fonti
2. **Identifica tendenze e novità** rilevanti
3. **Crea contenuto completamente originale** (NO copia-incolla)
4. **Fornisce valore pratico** per trader e investitori
5. **Usa un tono {style_guide.get(style, 'professional')}**

REQUISITI TECNICI:
- **Lingua**: {language_map.get(language, 'English')}{language_instructions.get(language, '')}
- **Lunghezza**: circa {max_length} parole
- **Formato**: HTML con tag <p>, <h2>, <h3>, <strong>, <em>, <ul>, <li>
- **Struttura**:
  - Titolo accattivante (H1 implicito)
  - Introduzione breve (2-3 frasi)
  - Corpo principale con sottosezioni (H2/H3)
  - Punti chiave/takeaway
  - Conclusione pratica

LINEE GUIDA CONTENUTO:
- Focus su **dati concreti e trend attuali**
- Cita numeri, percentuali, eventi specifici
- Evita generalizzazioni vaghe
- Linguaggio chiaro e preciso
- Rilevanza per il target (trader/investitori)

RISPOSTA RICHIESTA (JSON):
{{
  "title": "Titolo SEO-friendly (max 60 caratteri)",
  "meta_title": "Meta title per SEO (max 60 caratteri)",
  "meta_description": "Meta description (max 155 caratteri)",
  "meta_keywords": "keyword1, keyword2, keyword3, keyword4, keyword5",
  "excerpt": "Introduzione/summary 2-3 frasi",
  "content": "<p>Contenuto HTML completo...</p>",
  "read_time": {max(3, max_length // 200)},
  "key_points": ["punto chiave 1", "punto chiave 2", "punto chiave 3"]
}}

IMPORTANTE:
- Rispondi SOLO con il JSON valido, nient'altro
- NO testo prima del JSON
- NO testo dopo il JSON  
- NO markdown code blocks (```json)
- Inizia direttamente con {{ e termina con }}
- Usa virgolette doppie per JSON
- Escape caratteri speciali in HTML (&lt; &gt; &amp; &quot;)

Genera SOLO il JSON ora (inizia con {{):"""
        
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
        
        # Parse JSON from response (AI might add text before/after)
        try:
            # Try to find JSON in the response
            import re
            import json
            
            # Method 1: Find JSON object with regex
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
                try:
                    article_data = json.loads(json_str)
                    logger.info(f"✅ JSON parsed successfully")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON parse error: {e}")
                    logger.error(f"JSON string: {json_str[:500]}...")
                    
                    # Method 2: Try to fix common issues
                    # Remove markdown code blocks
                    json_str = re.sub(r'```json\s*', '', json_str)
                    json_str = re.sub(r'```\s*$', '', json_str)
                    
                    try:
                        article_data = json.loads(json_str)
                        logger.info(f"✅ JSON parsed after cleanup")
                    except:
                        logger.error(f"❌ Could not parse JSON even after cleanup")
                        return None
            else:
                logger.error(f"❌ No JSON found in response")
                logger.error(f"Response preview: {content[:500]}...")
                return None
            
            # Validate required fields
            required_fields = ['title', 'content']
            for field in required_fields:
                if field not in article_data:
                    logger.error(f"❌ Missing required field: {field}")
                    return None
            
            # Extract sources
            sources = [
                {'title': a.get('title'), 'link': a.get('link'), 'source': a.get('source')}
                for a in articles[:5]
            ]
            
            result = {
                'content': article_data.get('content', ''),
                'title': article_data.get('title', 'Untitled'),
                'excerpt': article_data.get('excerpt', ''),
                'meta_title': article_data.get('meta_title', article_data.get('title', '')),
                'meta_description': article_data.get('meta_description', article_data.get('excerpt', '')),
                'meta_keywords': article_data.get('meta_keywords', ''),
                'read_time': article_data.get('read_time', max(3, max_length // 200)),
                'key_points': article_data.get('key_points', []),
                'sources': sources,
                'ai_provider': ai_provider,
                'style': style,
                'language': language,
                'generated_at': datetime.utcnow().isoformat(),
                'word_count': len(article_data.get('content', '').split())
            }
            
            logger.info(f"✅ Article generated: {result['word_count']} words")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Raw response: {content[:1000]}...")
            return None
    
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

