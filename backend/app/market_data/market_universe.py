"""
Market Universe - Definisce tutti gli asset scansionabili
Organizzati per fonte dati e rate limits
"""

# ============================================
# CRYPTO - Binance (NO RATE LIMIT issues)
# ============================================
CRYPTO_SYMBOLS = [
    # Top 30 by Market Cap
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT',
    'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'LTC/USDT', 'ETC/USDT',
    'NEAR/USDT', 'ALGO/USDT', 'ICP/USDT', 'FIL/USDT', 'APT/USDT',
    'ARB/USDT', 'OP/USDT', 'INJ/USDT', 'SUI/USDT', 'SEI/USDT',
    'TIA/USDT', 'RENDER/USDT', 'WLD/USDT', 'RUNE/USDT', 'THETA/USDT'
]

# ============================================
# STOCKS - Finnhub (60 req/min LIMIT)
# Prioritizzati per importanza
# ============================================

# Tier 1: Top 15 (SEMPRE inclusi in scan)
STOCKS_TIER1 = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'AMZN',   # Amazon
    'NVDA',   # NVIDIA
    'META',   # Meta/Facebook
    'TSLA',   # Tesla
    'BRK.B',  # Berkshire Hathaway
    'JPM',    # JPMorgan
    'V',      # Visa
    'MA',     # Mastercard
    'WMT',    # Walmart
    'JNJ',    # Johnson & Johnson
    'PG',     # Procter & Gamble
    'XOM',    # Exxon Mobil
]

# Tier 2: Popular stocks (Quick Scan)
STOCKS_TIER2 = [
    'NFLX', 'DIS', 'PYPL', 'INTC', 'AMD', 'QCOM', 'CSCO', 'ORCL',
    'CRM', 'ADBE', 'AVGO', 'TXN', 'COST', 'PEP', 'KO', 'MCD',
    'NKE', 'BA', 'CAT', 'GE', 'F', 'GM', 'UBER', 'ABNB'
]

# Tier 3: Extended coverage (Full Scan only)
STOCKS_TIER3 = [
    'SBUX', 'HD', 'LOW', 'TGT', 'CVX', 'T', 'VZ', 'CMCSA',
    'PFE', 'ABBV', 'UNH', 'TMO', 'ABT', 'DHR', 'BMY', 'LLY',
    'BAC', 'WFC', 'GS', 'MS', 'C', 'SCHW', 'BLK', 'AXP'
]

# ============================================
# INDICES (as ETFs) - Finnhub
# ============================================
INDICES = [
    'SPY',   # S&P 500
    'QQQ',   # NASDAQ 100
    'DIA',   # Dow Jones
    'IWM',   # Russell 2000
    'VTI',   # Total Stock Market
    'VEA',   # Developed Markets ex-US
    'VWO',   # Emerging Markets
    'EFA',   # MSCI EAFE
]

# ============================================
# COMMODITIES (as ETFs) - Finnhub
# ============================================
COMMODITIES = [
    # Precious Metals
    'GLD',   # Gold
    'SLV',   # Silver
    'PPLT',  # Platinum
    'PALL',  # Palladium
    
    # Energy
    'USO',   # Crude Oil
    'BNO',   # Brent Oil
    'UNG',   # Natural Gas
    'UGA',   # Gasoline
    
    # Agriculture
    'CORN',  # Corn
    'WEAT',  # Wheat
    'SOYB',  # Soybeans
    
    # Industrial Metals
    'COPX',  # Copper Miners
    'SLX',   # Steel
]

# ============================================
# FOREX - OANDA (100 req/20sec = OK)
# ============================================
FOREX_MAJOR = [
    'EUR/USD',  # Euro/Dollar
    'GBP/USD',  # Pound/Dollar
    'USD/JPY',  # Dollar/Yen
    'USD/CHF',  # Dollar/Franc
    'AUD/USD',  # Aussie/Dollar
    'USD/CAD',  # Dollar/Canadian
    'NZD/USD',  # Kiwi/Dollar
]

FOREX_MINOR = [
    'EUR/GBP',  # Euro/Pound
    'EUR/JPY',  # Euro/Yen
    'GBP/JPY',  # Pound/Yen
    'EUR/CHF',  # Euro/Franc
    'AUD/JPY',  # Aussie/Yen
    'GBP/AUD',  # Pound/Aussie
    'EUR/AUD',  # Euro/Aussie
]

# ============================================
# SCAN PRESETS
# Ottimizzati per rate limits
# ============================================

SCAN_PRESETS = {
    # Quick Scan: ~55 simboli (Finnhub OK: 55 < 60/min)
    'quick': {
        'crypto': CRYPTO_SYMBOLS[:20],  # Top 20 crypto
        'stocks': STOCKS_TIER1,         # 15 top stocks
        'indices': INDICES[:5],         # 5 main indices
        'commodities': ['GLD', 'USO', 'SLV'],  # 3 main commodities
        'forex': FOREX_MAJOR[:5],       # 5 major pairs
        'total_finnhub_calls': 23,      # 15 + 5 + 3 = 23 (OK!)
        'estimated_time_sec': 30
    },
    
    # Balanced Scan: ~80 simboli (gestito con pause)
    'balanced': {
        'crypto': CRYPTO_SYMBOLS,       # Top 30 crypto
        'stocks': STOCKS_TIER1 + STOCKS_TIER2[:10],  # 25 stocks
        'indices': INDICES,             # 8 indices
        'commodities': COMMODITIES[:8], # 8 commodities
        'forex': FOREX_MAJOR,           # 7 pairs
        'total_finnhub_calls': 41,      # 25 + 8 + 8 = 41 (OK!)
        'estimated_time_sec': 60
    },
    
    # Full Scan: ~150 simboli (batch con pauses)
    'full': {
        'crypto': CRYPTO_SYMBOLS,       # 30 crypto
        'stocks': STOCKS_TIER1 + STOCKS_TIER2 + STOCKS_TIER3[:20],  # 59 stocks
        'indices': INDICES,             # 8 indices
        'commodities': COMMODITIES,     # 13 commodities
        'forex': FOREX_MAJOR + FOREX_MINOR[:5],  # 12 pairs
        'total_finnhub_calls': 80,      # 59 + 8 + 13 = 80
        'estimated_time_sec': 120,      # Con pause per rate limit
        'requires_batching': True
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_scan_symbols(preset: str = 'quick'):
    """
    Get symbols for a specific scan preset
    
    Returns:
        Dict with symbols organized by asset type
    """
    if preset not in SCAN_PRESETS:
        preset = 'quick'
    
    config = SCAN_PRESETS[preset]
    
    return {
        'crypto': [{'symbol': s, 'type': 'crypto'} for s in config['crypto']],
        'stocks': [{'symbol': s, 'type': 'stock'} for s in config['stocks']],
        'indices': [{'symbol': s, 'type': 'index'} for s in config['indices']],
        'commodities': [{'symbol': s, 'type': 'commodity'} for s in config['commodities']],
        'forex': [{'symbol': s, 'type': 'forex'} for s in config['forex']],
        'metadata': {
            'total_symbols': (
                len(config['crypto']) + 
                len(config['stocks']) + 
                len(config['indices']) + 
                len(config['commodities']) + 
                len(config['forex'])
            ),
            'finnhub_calls': config['total_finnhub_calls'],
            'estimated_time': config['estimated_time_sec'],
            'requires_batching': config.get('requires_batching', False)
        }
    }


def get_all_symbols_flat(preset: str = 'quick'):
    """
    Get flat list of all symbols with type annotation
    
    Returns:
        List of (symbol, type) tuples
    """
    data = get_scan_symbols(preset)
    symbols = []
    
    for asset_type in ['crypto', 'stocks', 'indices', 'commodities', 'forex']:
        for item in data[asset_type]:
            symbols.append((item['symbol'], item['type']))
    
    return symbols


def estimate_scan_time(num_symbols: int, includes_finnhub: int = 0) -> int:
    """
    Estimate scan time based on number of symbols
    
    Args:
        num_symbols: Total number of symbols
        includes_finnhub: Number of Finnhub calls
    
    Returns:
        Estimated time in seconds
    """
    # Base: 1 sec per symbol (analysis time)
    base_time = num_symbols * 1
    
    # Finnhub rate limit factor
    if includes_finnhub > 50:
        # Need to batch, add pause time
        batches = (includes_finnhub // 50) + 1
        pause_time = batches * 10  # 10 sec pause between batches
        base_time += pause_time
    
    return base_time

