# Trading Dashboard Mobile App

React Native app per ricevere e visualizzare best trades in tempo reale.

## 🚀 Setup Veloce

```bash
# Install dependencies
npm install

# iOS
cd ios && pod install && cd ..
npx react-native run-ios

# Android
npx react-native run-android
```

## 📱 Features

- ✅ Best Trades Dashboard
- ✅ Multi-Market Support (Crypto, Stocks, Forex, Commodities, Indices)
- ✅ Real-time notifications via Telegram Bot
- ✅ Category filtering
- ✅ Trade details with entry/stop/targets
- ✅ AI insights display
- ✅ Beautiful UI with animations

## 🔧 Configuration

Edit `src/config.ts`:

```typescript
export const API_URL = 'https://trading-dashboard-production-79d9.up.railway.app';
export const TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN';
export const TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID';
```

## 📂 Structure

```
mobile-app/
├── src/
│   ├── screens/
│   │   ├── HomeScreen.tsx          # Dashboard principale
│   │   ├── TradeDetailsScreen.tsx  # Dettagli trade
│   │   └── SettingsScreen.tsx      # Impostazioni
│   ├── components/
│   │   ├── TradeCard.tsx           # Card singola opportunità
│   │   ├── CategoryFilter.tsx      # Filtro categorie
│   │   └── ScanButton.tsx          # Bottone scan
│   ├── services/
│   │   ├── api.ts                  # API calls
│   │   └── telegram.ts             # Telegram integration
│   ├── types/
│   │   └── index.ts                # TypeScript types
│   └── config.ts                   # Configuration
├── App.tsx
└── package.json
```

## 🎯 API Integration

L'app si connette a:
- `GET /api/best-trades/scan?preset=quick`
- `GET /api/best-trades/analyze/{symbol}`
- `POST /api/telegram/notify/scan`

## 📲 Telegram Notifications

L'app può:
1. Triggerare scan dal backend
2. Ricevere notifiche push via Telegram Bot API
3. Mostrare opportunità in UI nativa

## 🎨 UI Components

- Categorizzazione per mercato
- Score colorato (verde > 80, giallo > 70, rosso < 60)
- Trade plan completo (Entry, Stop, Targets)
- Confluences display
- AI insights badge

