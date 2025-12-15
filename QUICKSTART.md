# ⚡ QUICKSTART - Get Running in 2 Minutes

## Step 1: Start the Dashboard

```bash
docker-compose up -d
```

Wait 30 seconds for everything to start...

## Step 2: Test It

```bash
# Run the test script
./test.sh

# OR manually test
curl http://localhost:8000/health
```

## Step 3: View API Docs

Open in browser: **http://localhost:8000/docs**

## Step 4: Try a Real API Call

```bash
# Get Bitcoin price (REAL DATA, no API key needed!)
curl "http://localhost:8000/api/market/price?symbol=BTC/USDT&exchange=binance"
```

## That's It! 🎉

Your backend is running with **REAL market data**.

---

## What's Next?

### Add API Keys (Optional)

Edit `.env` file:
```bash
nano .env
```

Add your keys:
- BINANCE_API_KEY (optional - public data works without it)
- OANDA_API_TOKEN (for forex data)
- FINNHUB_API_KEY (for stock data)
- ANTHROPIC_API_KEY (for AI features)

### Test with Your Keys

```bash
# Restart to load new keys
docker-compose restart backend

# Test all connections
curl http://localhost:8000/api/market/test
```

### View Logs

```bash
docker-compose logs -f backend
```

### Stop Everything

```bash
docker-compose down
```

---

## Troubleshooting

**Problem:** Port 8000 already in use
**Solution:** Change port in `docker-compose.yml` (line 42: `- "8001:8000"`)

**Problem:** API not responding
**Solution:** Check logs: `docker-compose logs backend`

**Problem:** Cannot connect to database
**Solution:** Restart: `docker-compose restart postgres`

---

**Ready to build the frontend?** Let me know! 🚀
