# AI Trading Bot with Claude

Modular Python trading bot that scans top 30 crypto pairs and sends AI-validated signals to Telegram.

## Features

- 📊 **Data Ingestion**: Fetches top 30 crypto pairs by 24h volume from Binance
- 🤖 **Claude AI Analysis**: Uses Anthropic Claude Sonnet 4 to validate setups
- 📱 **Telegram Alerts**: Sends top 3 high-confidence signals
- 🚀 **Railway Ready**: Includes Dockerfile and deployment config

## Setup

### 1. Environment Variables

Create `.env` file:

```env
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
ANTHROPIC_API_KEY=sk-ant-your-claude-key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=-1001234567890
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
uvicorn app.main:app --reload
```

### 4. Deploy to Railway

1. Connect your GitHub repo
2. Add environment variables in Railway dashboard
3. Deploy automatically

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - Detailed health status
- `POST /api/scan` - Run full market scan
- `GET /api/scan/quick/{symbol}` - Quick scan for single symbol
- `GET /api/test/telegram` - Test Telegram connection

## Usage

### Trigger Manual Scan

```bash
curl -X POST https://your-app.railway.app/api/scan
```

### Quick Symbol Scan

```bash
curl https://your-app.railway.app/api/scan/quick/BTC/USDT?timeframe=15m
```

## Architecture

```
app/
├── main.py                 # FastAPI app
├── config.py               # Settings
├── market_data/
│   └── binance_fetcher.py  # Binance data fetching
├── ai/
│   └── openai_vision.py    # GPT-4o Vision analysis
├── scanner/
│   └── scanner.py          # Main scanning logic
└── telegram/
    └── bot.py              # Telegram notifications
```

## Environment Variables Required on Railway

- `BINANCE_API_KEY`
- `BINANCE_SECRET`
- `ANTHROPIC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Optional:
- `TOP_N_COINS` (default: 30)
- `MIN_CONFIDENCE_SCORE` (default: 75)
- `MAX_ALERTS_PER_SCAN` (default: 3)

