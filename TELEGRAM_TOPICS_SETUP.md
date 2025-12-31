# 📱 TELEGRAM TOPICS SETUP GUIDE

## ✅ Sistema Implementato

Il tuo trading bot ora supporta **Telegram Topics** (Forum) per organizzare tutti i messaggi in un unico gruppo!

---

## 🎯 **TOPICS DISPONIBILI:**

```
🤖 AI Trading Bot (Telegram Group with Topics)
├─ 📊 Crypto Signals       → Segnali crypto (4H auto-scan)
├─ 🥇 Commodities Signals  → Segnali commodities (Gold, Oil, Silver, Wheat)
├─ 📈 Indices Signals       → Segnali indices (S&P 500, DAX, etc.)
├─ 📰 News & Articles       → Articoli AI generati automaticamente (3x/giorno)
├─ 📚 Education            → Contenuti educativi (future use)
└─ 💬 General Discussion   → Chat libera
```

---

## 🛠️ **COME CONFIGURARE TELEGRAM TOPICS**

### **Step 1: Crea un Supergroup Telegram**

1. Apri Telegram e crea un **nuovo gruppo**
2. Aggiungi almeno 1 altro membro (puoi rimuoverlo dopo)
3. Vai su **Impostazioni Gruppo** → **Tipo di Gruppo**
4. Converti in **Supergroup** (se non lo è già)

### **Step 2: Attiva Topics (Forum)**

1. Vai su **Impostazioni Gruppo**
2. Trova **"Topics"** o **"Forum"**
3. **Abilita Topics/Forum**
4. Il gruppo ora diventa un forum con topics!

### **Step 3: Crea i Topics**

Crea questi topics nel tuo gruppo:

1. **📊 Crypto Signals**
   - Descrizione: "Segnali di trading crypto da AI (4H)"
   - Icon: 📊

2. **🥇 Commodities Signals**
   - Descrizione: "Segnali commodities (Gold, Oil, Silver, Wheat)"
   - Icon: 🥇

3. **📈 Indices Signals**
   - Descrizione: "Segnali indici globali (S&P 500, DAX, etc.)"
   - Icon: 📈

4. **📰 News & Articles**
   - Descrizione: "Articoli AI generati da news finanziarie"
   - Icon: 📰

5. **📚 Education** (opzionale)
   - Descrizione: "Contenuti educativi e guide"
   - Icon: 📚

6. **💬 General** (opzionale)
   - Descrizione: "Discussioni generali"
   - Icon: 💬

### **Step 4: Ottieni i Topic IDs**

Per ottenere gli ID dei topics:

1. **Metodo 1 - Manuale (Raccomandato):**
   - Apri Telegram Desktop o Web
   - Vai su un topic
   - Guarda l'URL: `https://web.telegram.org/k/#-1234567890_123`
   - Il numero dopo `_` è il **Thread ID** (es: `123`)

2. **Metodo 2 - Automatico (Avanzato):**
   ```python
   # Invia un messaggio di test manualmente al topic
   # Il bot loggherà il message_thread_id
   ```

### **Step 5: Configura il Bot**

Aggiungi al tuo `.env` o chiama l'API:

```bash
# Opzionale: configurare topic IDs (se None, va in chat generale)
TELEGRAM_TOPIC_CRYPTO=123
TELEGRAM_TOPIC_COMMODITIES=456
TELEGRAM_TOPIC_INDICES=789
TELEGRAM_TOPIC_NEWS=101112
```

**Oppure** configura via API dopo deploy:

```bash
# Chiama questo endpoint per ogni topic
curl -X POST "https://your-backend.railway.app/api/telegram/set-topic" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_name": "crypto_signals",
    "thread_id": 123
  }'
```

### **Step 6: Aggiungi il Bot al Gruppo**

1. Vai su **@BotFather** su Telegram
2. Trova il tuo bot
3. Aggiungi il bot al gruppo
4. Dai al bot permessi di **Admin** con:
   - ✅ Post Messages
   - ✅ Delete Messages (opzionale)
   - ✅ Manage Topics

---

## 📋 **API ENDPOINT PER CONFIGURARE TOPICS**

### **Set Topic ID**
```http
POST /api/telegram/set-topic
Content-Type: application/json

{
  "topic_name": "crypto_signals",  // o commodities_signals, indices_signals, news_articles
  "thread_id": 123
}
```

### **Get Topic Configuration**
```http
GET /api/telegram/topics
```

Risposta:
```json
{
  "crypto_signals": 123,
  "commodities_signals": 456,
  "indices_signals": 789,
  "news_articles": 101112,
  "education": null,
  "general": null
}
```

---

## 🚀 **FEATURES IMPLEMENTATE**

### **1. Trading Signals (Auto-Scan)**
- ✅ **Crypto Signals** → Topic `crypto_signals`
  - Scan automatici ogni 4H (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)
  - Binance data (real-time)

- ✅ **Commodities Signals** → Topic `commodities_signals`
  - Scan automatici ogni 4H (+30min delay: 00:30, 04:30, etc.)
  - Yahoo Finance data (Gold, Oil, Silver, Wheat)

- ✅ **Indices Signals** → Topic `indices_signals`
  - Scan automatici ogni 4H (+1h delay: 01:00, 05:00, etc.)
  - Yahoo Finance data (S&P 500, DAX, FTSE, etc.)

### **2. News Articles (Auto-Generate & Post)**
- ✅ **News & Articles** → Topic `news_articles`
  - **3 articoli al giorno** generati automaticamente con AI:
    - 🌅 **09:00 Rome** (08:00 UTC) → **Crypto News**
    - 📊 **15:00 Rome** (14:00 UTC) → **Finance News**
    - 🌆 **19:00 Rome** (18:00 UTC) → **Tech News**
  
  - Fonti:
    - Crypto: CoinDesk, Cointelegraph, Decrypt, TheBlock, etc.
    - Finance: Reuters, Seeking Alpha, Investing.com, etc.
    - Tech: TechCrunch, The Verge, Ars Technica, etc.

### **3. Manual Article Generation**
- ✅ Dashboard `/news` per generare articoli manualmente
- ✅ Filtra per categoria, keyword, AI provider
- ✅ Preview e publish to Telegram
- ✅ Database storage (draft → published)

---

## 📊 **SCHEDULE COMPLETO**

```
⏰ ORARIO UTC → ORARIO ROMA (CET/CEST)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CRYPTO SIGNALS (Topic: crypto_signals)
00:00 UTC → 01:00 Rome
04:00 UTC → 05:00 Rome
08:00 UTC → 09:00 Rome ⭐
12:00 UTC → 13:00 Rome
16:00 UTC → 17:00 Rome
20:00 UTC → 21:00 Rome

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 COMMODITIES SIGNALS (Topic: commodities_signals)
00:30 UTC → 01:30 Rome
04:30 UTC → 05:30 Rome
08:30 UTC → 09:30 Rome
12:30 UTC → 13:30 Rome
16:30 UTC → 17:30 Rome
20:30 UTC → 21:30 Rome

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 INDICES SIGNALS (Topic: indices_signals)
01:00 UTC → 02:00 Rome
05:00 UTC → 06:00 Rome
09:00 UTC → 10:00 Rome
13:00 UTC → 14:00 Rome
17:00 UTC → 18:00 Rome
21:00 UTC → 22:00 Rome

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📰 NEWS ARTICLES (Topic: news_articles)
08:00 UTC → 09:00 Rome ⭐ (Crypto News)
14:00 UTC → 15:00 Rome ⭐ (Finance News)
18:00 UTC → 19:00 Rome ⭐ (Tech News)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 TRADE TRACKER (Background)
Every 15 minutes → Checks TP/SL on all open trades
```

---

## 🎨 **ESEMPIO STRUTTURA TELEGRAM**

```
🤖 AI Trading Bot
│
├─ 📊 Crypto Signals (123 messages)
│   ├─ 🟢 TRADING SIGNAL - BTC/USDT LONG
│   ├─ ✅ TRADE CLOSED - WIN +2.5%
│   └─ 🔴 TRADING SIGNAL - ETH/USDT SHORT
│
├─ 🥇 Commodities Signals (45 messages)
│   ├─ 🟢 TRADING SIGNAL - GOLD LONG
│   └─ 🟢 TRADING SIGNAL - OIL SHORT
│
├─ 📈 Indices Signals (67 messages)
│   ├─ 🟢 TRADING SIGNAL - S&P 500 LONG
│   └─ 🔴 TRADING SIGNAL - DAX SHORT
│
├─ 📰 News & Articles (89 messages)
│   ├─ 📰 Bitcoin Rally Continues... (09:00)
│   ├─ 📊 Fed Holds Rates Steady... (15:00)
│   └─ 💻 Apple Unveils New AI Features... (19:00)
│
├─ 📚 Education (5 messages)
│   └─ 📖 How to Read Trading Signals
│
└─ 💬 General (156 messages)
    └─ User discussions...
```

---

## 🔧 **TESTING**

### **Test Manual Article Generation**
```bash
# Via API
curl -X POST "http://localhost:8000/api/news/generate?category=crypto&ai_provider=claude&style=professional&language=it"
```

### **Test Article Publishing**
```bash
# Get article ID from generate response, then:
curl -X POST "http://localhost:8000/api/news/publish/1?topic=news_articles"
```

### **Test Manual Telegram Send**
```python
# In your backend code or Python shell:
from app.telegram import telegram

await telegram.send_article(
    {'content': 'Test article content'},
    topic='news_articles'
)
```

---

## ❓ **TROUBLESHOOTING**

### **1. Bot non invia messaggi ai topics**
- Verifica che il bot sia Admin con permesso "Manage Topics"
- Controlla che i Thread IDs siano corretti
- Guarda i log del backend per errori

### **2. Come trovo il Thread ID?**
- Metodo più semplice: usa Telegram Web/Desktop
- Apri il topic, guarda URL: il numero dopo `_` è il Thread ID

### **3. Posso usare un canale invece di un gruppo?**
- No, Topics funzionano solo in **Supergroups**
- Ma puoi continuare ad usare il vecchio sistema (senza topics)

### **4. Gli articoli non vengono generati automaticamente**
- Controlla i log: `Auto News Scheduler started`
- Verifica che `auto_news_scheduler` sia inizializzato in `main.py`
- Gli articoli vengono generati solo agli orari programmati (08:00, 14:00, 18:00 UTC)

---

## 🎉 **PRONTO!**

Ora hai un sistema completo con:
- ✅ Trading Signals organizzati per asset type
- ✅ News Articles automatici 3x/giorno
- ✅ Dashboard per gestire articoli
- ✅ Tutto in un unico Telegram Group con Topics!

**Enjoy your AI-powered trading & news system!** 🚀📰

