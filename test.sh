#!/bin/bash

echo "🧪 Testing Trading Dashboard Setup..."
echo ""

# Test 1: Check if containers are running
echo "1️⃣ Checking Docker containers..."
docker-compose ps

echo ""
echo "2️⃣ Testing API health..."
sleep 2
curl -s http://localhost:8000/health || echo "❌ API not responding"

echo ""
echo ""
echo "3️⃣ Testing Market Data (Binance - no API key needed)..."
curl -s "http://localhost:8000/api/market/price?symbol=BTC/USDT&exchange=binance" | python3 -m json.tool || echo "❌ Market data not working"

echo ""
echo ""
echo "✅ Setup test complete!"
echo ""
echo "📖 Open API docs: http://localhost:8000/docs"
echo "🔍 View logs: docker-compose logs -f backend"
