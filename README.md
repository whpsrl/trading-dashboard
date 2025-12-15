# 📊 Trading Dashboard - Quick Start Guide

## 🚀 Setup (5 Minutes)

### Prerequisites
- Docker and Docker Compose installed
- That's it! Docker handles everything else.

### Step 1: Get API Keys (Free)

**Binance (Crypto)** - Optional for now
1. Go to https://www.binance.com/
2. Create account → API Management
3. Copy API Key and Secret

**OANDA (Forex)** - Optional for now
1. Go to https://www.oanda.com/
2. Create practice account (free)
3. Get API token from Account → Manage API Access

**Finnhub (Stocks)** - Optional for now
1. Go to https://finnhub.io/register
2. Sign up (free)
3. Copy API key from dashboard

**Note:** You can start without API keys - Binance works without authentication for public data!

### Step 2: Configure Environment

```bash
# Edit .env file and add your API keys (or leave blank to start)
nano .env
```

### Step 3: Start Everything

```bash
# From project root directory
docker-compose up -d

# This starts:
# - PostgreSQL database (port 5432)
# - Redis cache (port 6379)
# - Backend API (port 8000)
```

### Step 4: Verify It's Running

```bash
# Check if containers are running
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs
```

## 🧪 Test the API

### Test Market Data Connection

```bash
# Test all data sources
curl http://localhost:8000/api/market/test

# Get BTC price from Binance (works without API key!)
curl "http://localhost:8000/api/market/price?symbol=BTC/USDT&exchange=binance"

# Get candlestick data
curl "http://localhost:8000/api/market/ohlcv?symbol=BTC/USDT&exchange=binance&timeframe=1h&limit=24"
```

### View in Browser

Go to: http://localhost:8000/docs

This opens the interactive API documentation where you can test all endpoints.

## 📁 Project Structure

```
trading-dashboard/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Application entry
│   │   ├── config.py    # Configuration
│   │   ├── database.py  # Database setup
│   │   └── market_data/ # Market data service
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Next.js frontend (coming next)
├── docker-compose.yml   # Docker configuration
└── .env                 # Environment variables
```

## 🛠️ Development Commands

```bash
# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop everything
docker-compose down

# Stop and remove all data
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Port already in use
```bash
# Find what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Change port in docker-compose.yml if needed
```

### Cannot connect to database
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### API returns errors
```bash
# Check backend logs
docker-compose logs backend

# Make sure .env file exists
cat .env
```

## ✅ What's Working Now

- ✅ Backend API running
- ✅ Database (PostgreSQL + TimescaleDB)
- ✅ Redis cache
- ✅ Market data from Binance (crypto) - NO API KEY NEEDED
- ✅ Market data from OANDA (forex) - needs API token
- ✅ Market data from Finnhub (stocks) - needs API key
- ✅ API documentation at /docs

## 🎯 Next Steps

1. **Test the API** - Make sure you can fetch BTC price
2. **Add API keys** - Optional, but needed for OANDA and Finnhub
3. **Build frontend** - Coming next (React/Next.js)
4. **Add AI analysis** - Claude integration
5. **Add indicators** - Custom technical indicators

## 📖 API Examples

### Get Real-Time Crypto Price
```bash
curl "http://localhost:8000/api/market/price?symbol=BTC/USDT&exchange=binance"

Response:
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "price": 43847.52,
  "volume_24h": 28400000000,
  "change_24h": 2.34,
  "timestamp": 1702656000000
}
```

### Get Candlestick Data
```bash
curl "http://localhost:8000/api/market/ohlcv?symbol=BTC/USDT&exchange=binance&timeframe=1h&limit=10"

Response:
[
  {
    "timestamp": 1702656000000,
    "open": 43800.00,
    "high": 43900.00,
    "low": 43750.00,
    "close": 43847.52,
    "volume": 1250.5
  },
  ...
]
```

## 📧 Support

If you run into issues:
1. Check the logs: `docker-compose logs`
2. Verify .env file is configured
3. Make sure Docker is running
4. Try rebuilding: `docker-compose up -d --build`

---

**Ready to continue?** Let me know and we'll build the frontend next! 🚀
