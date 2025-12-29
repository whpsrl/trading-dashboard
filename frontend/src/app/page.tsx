'use client'

import { useState } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function Home() {
  const [scanning, setScanning] = useState(false)
  const [message, setMessage] = useState('')
  const [results, setResults] = useState<any>(null)

  const runScan = async () => {
    setScanning(true)
    setMessage('🔍 Scanning top 30 crypto with AI Vision...')
    setResults(null)

    try {
      const response = await fetch(`${BACKEND_URL}/api/scan`, {
        method: 'POST',
      })

      const data = await response.json()

      if (data.status === 'started') {
        setMessage('✅ Scan started! Check Telegram for results in 2-3 minutes.')
      } else {
        setMessage('⚠️ Scan request sent. Results will be sent to Telegram.')
      }

      setResults(data)
    } catch (error) {
      setMessage('❌ Error: ' + (error as Error).message)
    } finally {
      setScanning(false)
    }
  }

  const testTelegram = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/test/telegram`)
      const data = await response.json()

      if (data.success) {
        setMessage('✅ Test alert sent to Telegram!')
      } else {
        setMessage('❌ Failed to send test alert')
      }
    } catch (error) {
      setMessage('❌ Error: ' + (error as Error).message)
    }
  }

  const checkHealth = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/health`)
      const data = await response.json()
      setResults(data)
      setMessage('✅ Health check complete')
    } catch (error) {
      setMessage('❌ Backend offline')
    }
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      background: 'white',
      borderRadius: '16px',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
    }}>
      <h1 style={{
        fontSize: '2.5rem',
        fontWeight: 'bold',
        marginBottom: '1rem',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        🤖 AI Trading Bot
      </h1>

      <p style={{
        fontSize: '1.1rem',
        color: '#666',
        marginBottom: '2rem'
      }}>
        GPT-4o Vision • Top 30 Crypto • Telegram Alerts
      </p>

      <div style={{
        display: 'grid',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <button
          onClick={runScan}
          disabled={scanning}
          style={{
            background: scanning ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '1.25rem 2rem',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            border: 'none',
            borderRadius: '12px',
            cursor: scanning ? 'not-allowed' : 'pointer',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={(e) => {
            if (!scanning) e.currentTarget.style.transform = 'scale(1.02)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)'
          }}
        >
          {scanning ? '⏳ Scanning...' : '🚀 START MARKET SCAN'}
        </button>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            onClick={testTelegram}
            style={{
              flex: 1,
              background: '#10b981',
              color: 'white',
              padding: '0.875rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            📱 Test Telegram
          </button>

          <button
            onClick={checkHealth}
            style={{
              flex: 1,
              background: '#6366f1',
              color: 'white',
              padding: '0.875rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            🏥 Health Check
          </button>
        </div>
      </div>

      {message && (
        <div style={{
          padding: '1rem',
          background: message.startsWith('✅') ? '#d1fae5' : message.startsWith('❌') ? '#fee2e2' : '#dbeafe',
          borderRadius: '8px',
          marginBottom: '1rem',
          fontSize: '0.95rem'
        }}>
          {message}
        </div>
      )}

      {results && (
        <div style={{
          padding: '1.5rem',
          background: '#f9fafb',
          borderRadius: '8px',
          fontSize: '0.875rem'
        }}>
          <h3 style={{ marginBottom: '0.75rem', fontWeight: 'bold' }}>Response:</h3>
          <pre style={{
            background: '#1f2937',
            color: '#10b981',
            padding: '1rem',
            borderRadius: '6px',
            overflow: 'auto',
            fontSize: '0.8rem'
          }}>
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}

      <div style={{
        marginTop: '2rem',
        padding: '1.5rem',
        background: '#f3f4f6',
        borderRadius: '8px',
        fontSize: '0.875rem'
      }}>
        <h3 style={{ fontWeight: 'bold', marginBottom: '0.75rem' }}>ℹ️ How it works:</h3>
        <ul style={{ listStyle: 'none', display: 'grid', gap: '0.5rem' }}>
          <li>1️⃣ Fetches top 30 crypto pairs from Binance by 24h volume</li>
          <li>2️⃣ Analyzes 300 candles on 15m, 1h, 4h timeframes</li>
          <li>3️⃣ GPT-4o Vision validates each setup with chart analysis</li>
          <li>4️⃣ Sends top 3 high-confidence signals to Telegram</li>
        </ul>
      </div>
    </div>
  )
}

