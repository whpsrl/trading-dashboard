"""
API routes for Stocks scanning with custom selection
"""
import logging
from fastapi import APIRouter, Query, Body
from typing import List, Dict

logger = logging.getLogger(__name__)

router = APIRouter()


# Popular stocks database - USA + Italy
STOCKS_DATABASE = {
    'usa_tech': {
        'name': '🇺🇸 Tech Giants',
        'stocks': [
            {'symbol': 'AAPL', 'name': 'Apple'},
            {'symbol': 'MSFT', 'name': 'Microsoft'},
            {'symbol': 'GOOGL', 'name': 'Alphabet (Google)'},
            {'symbol': 'AMZN', 'name': 'Amazon'},
            {'symbol': 'META', 'name': 'Meta (Facebook)'},
            {'symbol': 'NVDA', 'name': 'NVIDIA'},
            {'symbol': 'TSLA', 'name': 'Tesla'},
            {'symbol': 'NFLX', 'name': 'Netflix'},
            {'symbol': 'AMD', 'name': 'AMD'},
            {'symbol': 'INTC', 'name': 'Intel'},
        ]
    },
    'usa_finance': {
        'name': '🇺🇸 Finance',
        'stocks': [
            {'symbol': 'JPM', 'name': 'JP Morgan'},
            {'symbol': 'BAC', 'name': 'Bank of America'},
            {'symbol': 'WFC', 'name': 'Wells Fargo'},
            {'symbol': 'GS', 'name': 'Goldman Sachs'},
            {'symbol': 'MS', 'name': 'Morgan Stanley'},
            {'symbol': 'V', 'name': 'Visa'},
            {'symbol': 'MA', 'name': 'Mastercard'},
            {'symbol': 'BRK-B', 'name': 'Berkshire Hathaway'},
        ]
    },
    'usa_consumer': {
        'name': '🇺🇸 Consumer & Retail',
        'stocks': [
            {'symbol': 'WMT', 'name': 'Walmart'},
            {'symbol': 'HD', 'name': 'Home Depot'},
            {'symbol': 'NKE', 'name': 'Nike'},
            {'symbol': 'SBUX', 'name': 'Starbucks'},
            {'symbol': 'MCD', 'name': "McDonald's"},
            {'symbol': 'DIS', 'name': 'Disney'},
            {'symbol': 'COST', 'name': 'Costco'},
        ]
    },
    'usa_healthcare': {
        'name': '🇺🇸 Healthcare',
        'stocks': [
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson'},
            {'symbol': 'UNH', 'name': 'UnitedHealth'},
            {'symbol': 'PFE', 'name': 'Pfizer'},
            {'symbol': 'ABBV', 'name': 'AbbVie'},
            {'symbol': 'LLY', 'name': 'Eli Lilly'},
        ]
    },
    'usa_energy': {
        'name': '🇺🇸 Energy',
        'stocks': [
            {'symbol': 'XOM', 'name': 'Exxon Mobil'},
            {'symbol': 'CVX', 'name': 'Chevron'},
            {'symbol': 'COP', 'name': 'ConocoPhillips'},
        ]
    },
    'italy': {
        'name': '🇮🇹 Italia',
        'stocks': [
            {'symbol': 'ENI.MI', 'name': 'ENI'},
            {'symbol': 'ISP.MI', 'name': 'Intesa Sanpaolo'},
            {'symbol': 'UCG.MI', 'name': 'UniCredit'},
            {'symbol': 'ENEL.MI', 'name': 'Enel'},
            {'symbol': 'TIT.MI', 'name': 'Telecom Italia'},
            {'symbol': 'RACE.MI', 'name': 'Ferrari'},
            {'symbol': 'STLAM.MI', 'name': 'Stellantis'},
            {'symbol': 'G.MI', 'name': 'Generali'},
            {'symbol': 'LDO.MI', 'name': 'Leonardo'},
            {'symbol': 'TEN.MI', 'name': 'Tenaris'},
        ]
    }
}


@router.get("/list")
async def get_stocks_list():
    """Get available stocks organized by category"""
    try:
        return {
            "success": True,
            "categories": STOCKS_DATABASE
        }
    except Exception as e:
        logger.error(f"❌ Error getting stocks list: {e}")
        return {"success": False, "error": str(e)}


@router.post("/scan")
async def scan_stocks(
    ai_provider: str = Query("claude", pattern="^(claude|groq)$"),
    data: dict = Body(...)
):
    """
    Scan selected stocks on specified timeframes
    User selects which stocks to analyze
    
    Body format:
    {
        "selected_symbols": ["AAPL", "MSFT", ...],
        "timeframes": ["15m", "1h", "4h"]
    }
    """
    try:
        selected_symbols = data.get('selected_symbols', [])
        timeframes = data.get('timeframes', ['4h'])
        
        if not selected_symbols:
            return {"success": False, "error": "No stocks selected"}
        
        if not timeframes:
            return {"success": False, "error": "No timeframes selected"}
        
        from ..market_data.yahoo_fetcher import YahooFetcher
        from ..scanner.scanner import TradingScanner
        from ..config import settings
        from ..database.tracker import TradeTracker
        
        logger.info(f"📈 Starting STOCKS scan for {len(selected_symbols)} stocks with {ai_provider.upper()} AI...")
        logger.info(f"   Symbols: {', '.join(selected_symbols)}")
        logger.info(f"   Timeframes: {', '.join(timeframes)}")
        
        # Initialize fetcher
        yahoo_fetcher = YahooFetcher()
        
        # Initialize scanner with Yahoo fetcher
        scanner = TradingScanner(
            binance_key="",
            binance_secret="",
            claude_key=settings.ANTHROPIC_API_KEY,
            groq_key=settings.GROQ_API_KEY,
            top_n_coins=len(selected_symbols),
            min_confidence=settings.MIN_CONFIDENCE_SCORE
        )
        
        # Set AI provider
        scanner.set_ai_provider(ai_provider)
        
        # Replace Binance fetcher with Yahoo fetcher
        scanner.fetcher = yahoo_fetcher
        
        # Create scan session in database
        trade_tracker = TradeTracker()
        scan_id = trade_tracker.create_scan_session(
            scan_type='manual_stocks',
            top_n=len(selected_symbols),
            timeframes=timeframes,
            ai_provider=ai_provider
        )
        
        # Scan each stock on each timeframe
        all_setups = []
        for timeframe in timeframes:
            for symbol in selected_symbols:
                try:
                    # Get stock info (name)
                    symbol_info = yahoo_fetcher.get_symbol_info(symbol)
                    display_name = symbol_info['name'] if symbol_info else symbol
                    
                    logger.info(f"   Analyzing {display_name} ({symbol}) on {timeframe}...")
                    
                    # Fetch OHLCV data
                    ohlcv = await yahoo_fetcher.fetch_ohlcv(symbol, timeframe, limit=100)
                    
                    if not ohlcv or len(ohlcv) < 50:
                        logger.warning(f"   ⚠️ Insufficient data for {symbol}")
                        continue
                    
                    # Get current price
                    current_price = ohlcv[-1][4]
                    
                    # Get AI analysis
                    if ai_provider == 'claude':
                        analysis = await scanner.claude.analyze_setup(display_name, ohlcv, timeframe)
                    else:
                        analysis = await scanner.groq.analyze_setup(display_name, ohlcv, timeframe)
                    
                    if not analysis:
                        logger.warning(f"   ⚠️ No analysis returned for {symbol}")
                        continue
                    
                    confidence = analysis.get('confidence', 0)
                    
                    if confidence < settings.MIN_CONFIDENCE_SCORE:
                        logger.info(f"   {display_name} ({timeframe}): Low confidence ({confidence}%), skipping")
                        continue
                    
                    # Build setup
                    setup = {
                        'symbol': display_name,
                        'yahoo_symbol': symbol,
                        'timeframe': timeframe,
                        'direction': analysis.get('direction', 'NEUTRAL'),
                        'confidence': confidence,
                        'entry': analysis.get('entry', current_price),
                        'stop_loss': analysis.get('stop_loss', current_price * 0.95),
                        'take_profit': analysis.get('take_profit', current_price * 1.05),
                        'reasoning': analysis.get('reasoning', 'No reasoning provided'),
                        'market_strength': {
                            'score': 70,
                            'rating': '⚪ Neutral',
                            'reason': 'Stock market strength'
                        },
                        'ai_provider': ai_provider,
                        'market_type': 'stock'
                    }
                    
                    all_setups.append(setup)
                    logger.info(f"   ✅ {display_name} ({timeframe}): {setup['direction']} @ {confidence}%")
                    
                    # Save to database
                    trade_tracker.save_setup(setup, scan_id=scan_id)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error analyzing {symbol}: {e}")
                    continue
        
        # Sort by confidence
        all_setups.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        logger.info(f"✅ Stocks scan complete - found {len(all_setups)} setups")
        
        # Complete scan session
        high_conf_count = len([s for s in all_setups if s.get('confidence', 0) >= settings.MIN_CONFIDENCE_SCORE])
        trade_tracker.complete_scan_session(
            scan_id=scan_id,
            setups_count=len(all_setups),
            high_confidence_count=high_conf_count
        )
        
        return {
            "success": True,
            "scan_id": scan_id,
            "setups": all_setups,
            "count": len(all_setups),
            "high_confidence_count": high_conf_count,
            "scanned_stocks": len(selected_symbols),
            "timeframes": timeframes
        }
        
    except Exception as e:
        logger.error(f"❌ Stocks scan error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

