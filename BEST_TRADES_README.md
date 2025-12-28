# 🎯 AI Best Trades Finder

Sistema avanzato di analisi tecnica con AI per trovare le migliori opportunità di trading.

## ✨ Features

### 📊 Analisi Tecnica Multi-Indicatore
- **RSI** (Relative Strength Index) - Identifica condizioni di ipercomprato/ipervenduto
- **MACD** (Moving Average Convergence Divergence) - Segnali di momentum
- **Bollinger Bands** - Volatilità e breakout
- **EMA/SMA** (20, 50, 200) - Trend analysis
- **ATR** (Average True Range) - Volatilità per stop loss
- **Stochastic Oscillator** - Momentum
- **Volume Profile** - Conferma dei movimenti
- **Support/Resistance** - Livelli chiave automatici
- **Trend Strength** - Forza e consistenza del trend

### 🤖 AI Validation con Claude Sonnet 4
- Validazione automatica dei setup con score > 60
- Analisi di rischio avanzata
- Insights e raccomandazioni personalizzate
- Identificazione di pattern complessi

### 🎯 Sistema di Scoring Intelligente
- **Score 0-100** basato su confluenze tecniche
- **Direction** - LONG/SHORT/NEUTRAL con confidence %
- **Multi-factor analysis** - Peso diverso per ogni indicatore
- **Confluenze** - Lista dei fattori che confermano il setup
- **Warnings** - Segnali contrastanti identificati

### 📈 Piano di Trading Automatico
- **Entry** - Calcolato in base al prezzo corrente e livelli S/R
- **Stop Loss** - Basato su ATR e support/resistance
- **Target 1 & 2** - Obiettivi multipli con R:R ratio
- **Risk %** - Percentuale di rischio sul capitale
- **R:R Ratio** - Risk/Reward per ogni target

## 🚀 Quick Start

### Backend API

```bash
# Installa dipendenze
cd backend
pip install -r requirements.txt

# Configura .env
ANTHROPIC_API_KEY=your_api_key_here

# Avvia server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Apri http://localhost:3000/best-trades

## 📡 API Endpoints

### Analizza Singolo Simbolo

```bash
GET /api/best-trades/analyze/{symbol}?exchange=binance&timeframe=1h

# Esempio
curl "http://localhost:8000/api/best-trades/analyze/BTC/USDT?timeframe=1h"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "BTC/USDT",
    "score": 75.5,
    "direction": "LONG",
    "confidence": 82.3,
    "current_price": 43500.00,
    "trade_levels": {
      "entry": 43500.00,
      "stop_loss": 42800.00,
      "target_1": 44500.00,
      "target_2": 45200.00,
      "risk_reward_ratio_t1": 2.5,
      "risk_reward_ratio_t2": 3.8,
      "risk_percent": 1.6
    },
    "confluences": [
      "RSI: RSI oversold at 28.5",
      "MACD: MACD bullish crossover",
      "BOLLINGER: Price at lower BB",
      "TREND: Uptrend (strength: 68, consistency: 75)"
    ],
    "warnings": [],
    "ai_insights": {
      "valid": true,
      "validation_score": 8,
      "recommendation": "Strong bullish setup with multiple confluences...",
      "risk_factors": ["High volatility period"],
      "opportunities": ["Bounce from support", "Volume increasing"]
    }
  }
}
```

### Scan Mercato Completo

```bash
GET /api/best-trades/scan?min_score=60&timeframe=1h

# Scan personalizzato
GET /api/best-trades/scan?min_score=70&symbols=BTC/USDT,ETH/USDT,SOL/USDT
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "opportunities": [
    { "symbol": "BTC/USDT", "score": 85.2, ... },
    { "symbol": "ETH/USDT", "score": 78.5, ... },
    ...
  ],
  "scan_time": "2025-12-28T10:30:00",
  "message": "Found 5 opportunities with score >= 60"
}
```

### Top Opportunities (Quick Scan)

```bash
GET /api/best-trades/top?limit=5

# Esempio
curl "http://localhost:8000/api/best-trades/top?limit=10&timeframe=4h"
```

## 🧮 Come Funziona il Scoring

### Componenti del Score (Totale: 100 punti)

1. **RSI** (max 30 punti)
   - Oversold (<30) = Bullish
   - Overbought (>70) = Bearish
   - Score aumenta con la distanza dalle zone estreme

2. **MACD** (max 30 punti)
   - Crossover bullish/bearish = 20 punti
   - Histogram strength = 10 punti

3. **Bollinger Bands** (max 25 punti)
   - Tocco banda inferiore = Bullish (25 punti)
   - Tocco banda superiore = Bearish (25 punti)
   - BB Squeeze = +10 punti (setup pre-breakout)

4. **Trend** (max 20 punti)
   - Direction: uptrend/downtrend
   - Strength: 0-100
   - Consistency: R-squared del trend

5. **Volume** (max 15 punti)
   - Volume > avg + 50% = 15 punti
   - Volume > avg + 20% = 10 punti
   - Volume trend increasing = +5 punti

6. **Support/Resistance** (max 20 punti)
   - Prezzo vicino a S/R (< 2%) = 20 punti

### Determinazione Direction

- **LONG**: Score bullish > score bearish AND score bullish > 30
- **SHORT**: Score bearish > score bullish AND score bearish > 30
- **NEUTRAL**: Nessuna direzione chiara o score totale < 50

### Confidence Calculation

```
confidence = (winning_score / (bullish_score + bearish_score)) * 100
```

## 🎨 Frontend UI

### Pagina Best Trades

- **Quick Scan** - Scansiona top 20 crypto in ~30 secondi
- **Full Scan** - Scansiona top 30 crypto con filtro min score
- **Filtro Score** - Imposta soglia minima (0-100)
- **Cards Interattive** - Ogni opportunità mostra:
  - Score colorato (verde > 80, giallo > 70, rosso < 60)
  - Direction e Confidence
  - Piano di trading completo
  - Confluenze e warnings
  - AI insights (se disponibili)

### Componente BestTradesFinder

```tsx
import BestTradesFinder from '@/components/BestTradesFinder';

<BestTradesFinder apiUrl="http://localhost:8000" />
```

## 🔧 Configurazione

### Environment Variables

```bash
# Backend (.env)
ANTHROPIC_API_KEY=sk-ant-xxx  # Necessario per AI validation
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Parametri Personalizzabili

Nel file `backend/app/best_trades/scoring.py`:

```python
# Modifica soglie e pesi
RSI_OVERSOLD = 30  # Default
RSI_OVERBOUGHT = 70
MIN_SCORE_FOR_AI_VALIDATION = 60
```

## 📊 Esempi di Uso

### Trova Best Trade su BTC

```python
import requests

response = requests.get(
    "http://localhost:8000/api/best-trades/analyze/BTC/USDT",
    params={"timeframe": "1h"}
)

data = response.json()['data']

print(f"Score: {data['score']}")
print(f"Direction: {data['direction']}")
print(f"Entry: ${data['trade_levels']['entry']}")
print(f"Target 1: ${data['trade_levels']['target_1']} (R:R {data['trade_levels']['risk_reward_ratio_t1']}:1)")
```

### Scan Mercato con Python

```python
response = requests.get(
    "http://localhost:8000/api/best-trades/scan",
    params={
        "min_score": 70,
        "timeframe": "4h"
    }
)

opportunities = response.json()['opportunities']

for opp in opportunities[:5]:
    print(f"{opp['symbol']}: {opp['score']:.1f} - {opp['direction']}")
```

### Integrazione con Trading Bot

```python
async def find_and_execute_trades():
    # 1. Scan mercato
    response = await client.get("/api/best-trades/top?limit=3")
    opportunities = response.json()['opportunities']
    
    for opp in opportunities:
        if opp['score'] >= 80 and opp['confidence'] >= 75:
            # 2. Valida con AI
            if opp.get('ai_insights', {}).get('valid', False):
                # 3. Esegui trade
                await execute_trade(
                    symbol=opp['symbol'],
                    direction=opp['direction'],
                    entry=opp['trade_levels']['entry'],
                    stop_loss=opp['trade_levels']['stop_loss'],
                    target=opp['trade_levels']['target_1']
                )
```

## ⚠️ Disclaimer

Questo è uno strumento di analisi tecnica con AI per scopi **educativi e informativi**.

- ❌ **NON è financial advice**
- ❌ **NON garantisce profitti**
- ✅ Fai sempre la tua analisi
- ✅ Gestisci il rischio appropriatamente
- ✅ Usa solo capitale che puoi permetterti di perdere

## 📈 Performance Tips

### Backend Optimization

1. **Rate Limiting**: Implementa delay tra le richieste per evitare ban
2. **Caching**: Usa Redis per cachare i risultati (TTL 5-10 min)
3. **Parallel Processing**: Aumenta `max_concurrent` nel scanner
4. **Database**: Salva analisi storiche per ML training

### Frontend Optimization

1. **Polling**: Evita di chiamare scan continuamente
2. **Pagination**: Mostra risultati in pagine se > 20
3. **WebSocket**: Per aggiornamenti real-time
4. **Service Worker**: Cache delle analisi recenti

## 🛠️ Development

### Run Tests

```bash
cd backend
pytest tests/test_best_trades.py -v
```

### Add New Indicator

1. Aggiungi calcolo in `backend/app/indicators/technical.py`
2. Aggiungi scoring in `backend/app/best_trades/scoring.py`
3. Update `calculate_all()` e `calculate_total_score()`

### Custom Scoring Strategy

```python
# Crea nuova strategia
class ConservativeScorer(TradeScorer):
    @staticmethod
    def score_rsi(rsi):
        # Più conservativo
        if rsi < 25:  # Solo RSI molto oversold
            return {'score': 40, 'signal': 'bullish', ...}
        return {'score': 0, 'signal': 'neutral', ...}
```

## 📚 Resources

- [Technical Analysis Documentation](./docs/technical_analysis.md)
- [API Reference](./docs/api_reference.md)
- [Scoring System Details](./docs/scoring_system.md)

## 🤝 Contributing

Contributi benvenuti! Vedi [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

MIT License - vedi [LICENSE](./LICENSE)

---

**Built with ❤️ using FastAPI, Claude AI, and Next.js**

