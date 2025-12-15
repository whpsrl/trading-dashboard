# 🚀 DEPLOY SU VERCEL + RAILWAY - GUIDA COMPLETA

## ⏱️ Tempo Totale: 15 minuti

---

## 📋 PREREQUISITI

Prima di iniziare, crea questi account (tutti gratuiti):

1. **GitHub**: https://github.com/signup
2. **Railway**: https://railway.app/
3. **Vercel**: https://vercel.com/signup

Avrai bisogno di:
- ✅ Email
- ✅ Carta di credito/debito per Railway (dopo trial gratuito)

---

## PARTE 1: UPLOAD SU GITHUB (5 minuti)

### Step 1: Crea Repository su GitHub

1. Vai su https://github.com/new
2. Repository name: `trading-dashboard`
3. Visibility: **Private** (raccomandato) o Public
4. ❌ NON aggiungere README, .gitignore, license (già presenti)
5. Click **"Create repository"**

### Step 2: Upload Codice

**Opzione A: Da Terminale (se hai Git)**

```bash
cd C:\trading-dashboard

# Inizializza Git
git init

# Aggiungi file
git add .

# Commit
git commit -m "Initial commit - Trading Dashboard"

# Collega a GitHub (sostituisci USERNAME con il tuo)
git remote add origin https://github.com/USERNAME/trading-dashboard.git

# Push
git branch -M main
git push -u origin main
```

**Opzione B: Upload Manuale (più semplice)**

1. Vai al tuo repository su GitHub
2. Click **"uploading an existing file"**
3. Trascina la cartella `trading-dashboard` completa
4. Click **"Commit changes"**

✅ **Verificato:** Vai su GitHub e vedi tutti i file

---

## PARTE 2: DEPLOY BACKEND SU RAILWAY (5 minuti)

### Step 1: Crea Progetto Railway

1. Vai su https://railway.app/
2. Click **"Start a New Project"**
3. Scegli **"Deploy from GitHub repo"**
4. Autorizza Railway ad accedere a GitHub
5. Seleziona repository: **trading-dashboard**

### Step 2: Configura Backend

Railway rileva automaticamente il Dockerfile. Se chiede:
- **Root Directory**: `/backend`
- **Start Command**: Lascia vuoto (usa quello nel Dockerfile)

### Step 3: Aggiungi Database

1. Nel tuo progetto Railway, click **"+ New"**
2. Seleziona **"Database" → "Add PostgreSQL"**
3. Railway crea database automaticamente ✅

### Step 4: Aggiungi Redis

1. Click **"+ New"** di nuovo
2. Seleziona **"Database" → "Add Redis"**
3. Railway crea Redis automaticamente ✅

### Step 5: Configura Environment Variables

1. Click sul servizio **backend** (quello con il codice)
2. Tab **"Variables"**
3. Aggiungi queste variabili:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ENCRYPTION_KEY=your-32-character-encryption-key-here-minimum
BINANCE_API_KEY=(lascia vuoto per ora - funziona comunque)
BINANCE_API_SECRET=(lascia vuoto per ora)
OANDA_API_TOKEN=(lascia vuoto per ora)
FINNHUB_API_KEY=(lascia vuoto per ora)
ANTHROPIC_API_KEY=(lascia vuoto per ora)
ENVIRONMENT=production
DEBUG=false
```

**NOTA:** `${{Postgres.DATABASE_URL}}` e `${{Redis.REDIS_URL}}` sono automatici - Railway li collega!

### Step 6: Deploy!

1. Click **"Deploy"**
2. Attendi 2-3 minuti per il build
3. Una volta completato, vedrai **"Active"** ✅

### Step 7: Ottieni URL Backend

1. Nel servizio backend, tab **"Settings"**
2. Sezione **"Domains"**
3. Click **"Generate Domain"**
4. Copia l'URL generato, tipo:
   ```
   https://trading-dashboard-production.up.railway.app
   ```

✅ **Test Backend:**
```
https://YOUR-BACKEND-URL/health
```

Dovresti vedere: `{"status":"healthy"}`

---

## PARTE 3: DEPLOY FRONTEND SU VERCEL (5 minuti)

### Step 1: Importa Progetto

1. Vai su https://vercel.com/
2. Click **"Add New..." → "Project"**
3. Seleziona **"Import Git Repository"**
4. Scegli il tuo repo: **trading-dashboard**
5. Click **"Import"**

### Step 2: Configura Build

Vercel rileva Next.js automaticamente:
- **Framework Preset**: Next.js
- **Root Directory**: `frontend` ← **IMPORTANTE!**
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

### Step 3: Aggiungi Environment Variable

Nella sezione **"Environment Variables"**:

```
Nome: NEXT_PUBLIC_API_URL
Valore: https://YOUR-BACKEND-URL (quello di Railway)
```

**Esempio:**
```
NEXT_PUBLIC_API_URL=https://trading-dashboard-production.up.railway.app
```

### Step 4: Deploy!

1. Click **"Deploy"**
2. Attendi 1-2 minuti per il build
3. Una volta completato, vedrai **"Visit"** ✅

### Step 5: Ottieni URL

Vercel assegna automaticamente URL tipo:
```
https://trading-dashboard-USERNAME.vercel.app
```

✅ **Testa Dashboard:**

Apri l'URL - dovresti vedere:
- Dashboard con design scuro/blu
- Prezzo Bitcoin REALE aggiornato ogni 5 secondi
- Badge "LIVE - Real Market Data"

---

## ✅ VERIFICA COMPLETA

### Test 1: Backend Funziona

```bash
curl https://YOUR-BACKEND-URL/health

# Risposta: {"status":"healthy"}
```

### Test 2: Dati Reali

```bash
curl "https://YOUR-BACKEND-URL/api/market/price?symbol=BTC/USDT&exchange=binance"

# Risposta: {"symbol":"BTC/USDT","price":43500,...}
```

### Test 3: Frontend Connesso

Apri: `https://YOUR-FRONTEND-URL`

Dovresti vedere:
- ✅ Prezzo Bitcoin real-time
- ✅ Aggiornamento ogni 5 secondi
- ✅ Design professionale

---

## 💰 COSTI

### Railway
- **Trial**: $5 gratis
- **Dopo trial**: ~$5-10/mese
  - Database PostgreSQL: $5/mese
  - Redis: incluso
  - Backend: $0-5/mese (500 ore gratis/mese)

### Vercel
- **Frontend**: GRATIS ✅
- **Tutto incluso**: Deploy, SSL, CDN, bandwidth

### TOTALE: $5-10/mese

---

## 🔧 TROUBLESHOOTING

### Problema: "Build Failed" su Railway

**Soluzione:**
1. Verifica che `backend/Dockerfile` esista
2. Controlla logs: click su build → vedi errore
3. Verifica Root Directory sia `/backend`

### Problema: "Build Failed" su Vercel

**Soluzione:**
1. Verifica Root Directory sia `frontend`
2. Verifica che `frontend/package.json` esista
3. Controlla logs deploy

### Problema: Frontend mostra "Failed to fetch"

**Soluzione:**
1. Verifica `NEXT_PUBLIC_API_URL` sia configurata
2. Testa backend URL manualmente
3. Verifica CORS nel backend

### Problema: Database Connection Error

**Soluzione:**
1. Verifica `DATABASE_URL` nelle environment variables
2. Controlla che PostgreSQL sia "Active" su Railway
3. Usa la variabile di riferimento: `${{Postgres.DATABASE_URL}}`

---

## 🎯 DOPO IL DEPLOY

### Deploy Automatico

Ora ogni volta che fai:
```bash
git push origin main
```

➡️ Railway E Vercel deploysno automaticamente! 🚀

### Aggiungi API Keys

Quando hai le API keys:
1. Railway → Backend → Variables
2. Aggiungi:
   - `OANDA_API_TOKEN`
   - `FINNHUB_API_KEY`
   - `ANTHROPIC_API_KEY`
3. Railway re-deploya automaticamente

### Dominio Custom (Opzionale)

**Vercel:**
1. Settings → Domains
2. Aggiungi tuo dominio
3. Segui istruzioni DNS

**Railway:**
1. Settings → Domains
2. Aggiungi custom domain
3. Configura DNS

---

## 📊 MONITORING

### Railway Dashboard
- CPU/Memory usage
- Logs in real-time
- Deploy history

### Vercel Dashboard
- Analytics
- Performance metrics
- Edge functions stats

---

## 🎉 CONGRATULAZIONI!

Hai online:
- ✅ Backend FastAPI su Railway
- ✅ Database PostgreSQL + Redis
- ✅ Frontend Next.js su Vercel
- ✅ Deploy automatico da GitHub
- ✅ SSL/HTTPS gratis
- ✅ Dati market REALI

**URLs:**
- Frontend: `https://trading-dashboard-USERNAME.vercel.app`
- Backend: `https://trading-dashboard-production.up.railway.app`

**Mostra a chiunque!** 🚀

---

## 🚀 PROSSIMI PASSI

Ora che è online, possiamo aggiungere:
1. AI Chat integration (Claude)
2. Chart component con grafici
3. Custom indicators
4. Authentication system
5. WebSocket real-time
6. Alert system

**Dimmi cosa vuoi aggiungere dopo!**
