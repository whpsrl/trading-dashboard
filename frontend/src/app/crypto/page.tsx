'use client'

import { useState } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function CryptoPage() {
  const [scanning, setScanning] = useState(false)
  const [message, setMessage] = useState('')
  const [results, setResults] = useState<any>(null)

  const runScan = async () => {
    setScanning(true)
    setMessage('🔍 Scanning top 15 crypto with Claude AI...')
    setResults(null)

    try {
      const response = await fetch(`${BACKEND_URL}/api/scan`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()

      if (data.status === 'started') {
        setMessage('✅ Scan started! Check Telegram for results in 2-3 minutes.')
      } else if (data.error) {
        setMessage('❌ ' + data.error)
      } else {
        setMessage('⚠️ Scan request sent. Results will be sent to Telegram.')
      }

      setResults(data)
    } catch (error) {
      setMessage('❌ Failed to scan market: ' + (error as Error).message)
      console.error('Scan error:', error)
    } finally {
      setScanning(false)
    }
  }

  const testBTC = async () => {
    setMessage('🧪 Testing BTC analysis...')
    try {
      const response = await fetch(`${BACKEND_URL}/api/scan/test`)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const data = await response.json()
      setResults(data)
      
      if (data.success) {
        setMessage('✅ BTC analysis complete!')
      } else {
        setMessage('⚠️ ' + (data.error || 'Analysis failed'))
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
      maxWidth: '900px',
      margin: '0 auto',
      padding: '0 1.5rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2.5rem',
        boxShadow: '0 20px 60px rgba(0,0,0,0.15)'
      }}>
        <h1 style={{
          fontSize: '2.25rem',
          fontWeight: 'bold',
          marginBottom: '0.75rem',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🚀 Crypto Scanner
        </h1>

        <p style={{
          fontSize: '1rem',
          color: '#666',
          marginBottom: '2rem'
        }}>
          Claude Sonnet 4 • Top 15 Crypto • Telegram Alerts
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

          <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: '1fr 1fr' }}>
            <button
              onClick={checkHealth}
              style={{
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

            <button
              onClick={testBTC}
              style={{
                background: '#f59e0b',
                color: 'white',
                padding: '0.875rem',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              🧪 Test BTC
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
              fontSize: '0.8rem',
              maxHeight: '400px'
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
            <li>1️⃣ Fetches top 15 crypto pairs from Binance by 24h volume</li>
            <li>2️⃣ Analyzes 300 candles on 15m, 1h, 4h timeframes</li>
            <li>3️⃣ Claude Sonnet 4 validates each setup (min 60% confidence)</li>
            <li>4️⃣ Sends top 3 signals to Telegram with Entry/TP/SL</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

