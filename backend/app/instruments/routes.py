"""
Instruments endpoint - returns all available trading pairs
"""
from fastapi import APIRouter, HTTPException
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/instruments", tags=["instruments"])

@router.get("/binance")
async def get_binance_instruments():
    """
    Get all available trading pairs from Binance
    Returns all USDT pairs
    """
    try:
        # Call Binance public API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.binance.com/api/v3/exchangeInfo",
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Binance API error")
            
            data = response.json()
            
            # Filter only USDT pairs that are trading
            usdt_symbols = []
            for symbol_info in data.get('symbols', []):
                if (symbol_info.get('symbol', '').endswith('USDT') and 
                    symbol_info.get('status') == 'TRADING' and
                    symbol_info.get('quoteAsset') == 'USDT'):
                    
                    base_asset = symbol_info.get('baseAsset', '')
                    symbol = symbol_info.get('symbol', '')
                    
                    usdt_symbols.append({
                        'symbol': symbol,
                        'name': f"{base_asset}/USDT",
                        'baseAsset': base_asset,
                        'quoteAsset': 'USDT'
                    })
            
            logger.info(f"✅ Loaded {len(usdt_symbols)} Binance USDT pairs")
            
            return {
                "success": True,
                "count": len(usdt_symbols),
                "instruments": usdt_symbols
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Binance API timeout")
    except Exception as e:
        logger.error(f"❌ Failed to load Binance instruments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load instruments: {str(e)}")
