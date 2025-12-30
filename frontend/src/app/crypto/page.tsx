'use client'

import { useState } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function CryptoPage() {
  const [scanning, setScanning] = useState(false)
  const [message, setMessage] = useState('')
  const [results, setResults] = useState<any>(null)
  const [cryptoCount, setCryptoCount] = useState(15)

  const runScan = async () => {
    setScanning(true)
    setMessage('🔍 Scanning top 15 crypto with Claude AI...')
    setResults(null)

    try {
      console.log('🚀 Calling:', `${BACKEND_URL}/api/scan?top_n=${cryptoCount}`)
      
      const response = await fetch(`${BACKEND_URL}/api/scan?top_n=${cryptoCount}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      console.log('📡 Response status:', response.status)
      console.log('📡 Response ok:', response.ok)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Error response:', errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('✅ Response data:', data)

      if (data.success) {
        setMessage(`✅ Scan complete! Found ${data.count} high-confidence setups`)
        setResults(data.setups || [])
      } else if (data.error) {
        setMessage('❌ ' + data.error)
        setResults(null)
      } else {
        setMessage('⚠️ ' + (data.message || 'Unknown response'))
        setResults(data)
      }
    } catch (error) {
      console.error('❌ Full error:', error)
      setMessage('❌ Failed to scan market: ' + (error as Error).message)
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
          marginBottom: '1rem'
        }}>
          Claude Sonnet 4 • Multi-Timeframe Analysis • Telegram Alerts
        </p>

        {/* Crypto Count Selector */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          marginBottom: '1.5rem',
          padding: '1rem',
          background: '#f9fafb',
          borderRadius: '8px'
        }}>
          <label style={{ fontSize: '0.95rem', fontWeight: '600', color: '#374151' }}>
            🎯 Crypto to scan:
          </label>
          <select 
            value={cryptoCount}
            onChange={(e) => setCryptoCount(Number(e.target.value))}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: '2px solid #e5e7eb',
              fontSize: '0.95rem',
              fontWeight: '600',
              cursor: 'pointer',
              background: 'white'
            }}
          >
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
            <option value={15}>Top 15</option>
          </select>
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            by 24h volume
          </span>
        </div>

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

        {results && Array.isArray(results) && results.length > 0 && (
          <div style={{ marginTop: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>
              📊 Found {results.length} Setups
            </h2>
            
            <div style={{
              display: 'grid',
              gap: '1rem',
              gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))'
            }}>
              {results.map((setup: any, idx: number) => (
                <div key={idx} style={{
                  background: 'white',
                  border: '2px solid ' + (setup.direction === 'LONG' ? '#10b981' : setup.direction === 'SHORT' ? '#ef4444' : '#6b7280'),
                  borderRadius: '12px',
                  padding: '1.25rem',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}>
                  {/* Header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>
                      {setup.symbol}
                    </h3>
                    <span style={{
                      background: setup.direction === 'LONG' ? '#d1fae5' : setup.direction === 'SHORT' ? '#fee2e2' : '#e5e7eb',
                      color: setup.direction === 'LONG' ? '#065f46' : setup.direction === 'SHORT' ? '#991b1b' : '#374151',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px',
                      fontSize: '0.875rem',
                      fontWeight: 'bold'
                    }}>
                      {setup.direction}
                    </span>
                  </div>

                  {/* Timeframe & Confidence */}
                  <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
                    <span style={{
                      background: '#dbeafe',
                      color: '#1e40af',
                      padding: '0.25rem 0.625rem',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      fontWeight: '600'
                    }}>
                      ⏰ {setup.timeframe}
                    </span>
                    <span style={{
                      background: '#fef3c7',
                      color: '#92400e',
                      padding: '0.25rem 0.625rem',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      fontWeight: '600'
                    }}>
                      🎯 {setup.confidence}%
                    </span>
                  </div>

                  {/* Price Levels */}
                  <div style={{
                    background: '#f9fafb',
                    padding: '0.875rem',
                    borderRadius: '8px',
                    marginBottom: '1rem',
                    fontSize: '0.875rem'
                  }}>
                    <div style={{ display: 'grid', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#6b7280' }}>💰 Entry:</span>
                        <span style={{ fontWeight: 'bold' }}>${setup.entry?.toFixed(2)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#10b981' }}>🎯 Take Profit:</span>
                        <span style={{ fontWeight: 'bold', color: '#10b981' }}>${setup.take_profit?.toFixed(2)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#ef4444' }}>🛡️ Stop Loss:</span>
                        <span style={{ fontWeight: 'bold', color: '#ef4444' }}>${setup.stop_loss?.toFixed(2)}</span>
                      </div>
                      {setup.current_price && (
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '0.5rem', borderTop: '1px solid #e5e7eb' }}>
                          <span style={{ color: '#6b7280' }}>Current:</span>
                          <span style={{ fontWeight: 'bold' }}>${setup.current_price?.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* AI Reasoning */}
                  <div style={{
                    background: '#eff6ff',
                    padding: '0.875rem',
                    borderRadius: '8px',
                    fontSize: '0.8rem',
                    lineHeight: '1.5',
                    color: '#1e40af'
                  }}>
                    <strong>🤖 AI Analysis:</strong><br />
                    {setup.reasoning}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {results && Array.isArray(results) && results.length === 0 && (
          <div style={{
            padding: '2rem',
            background: '#fef3c7',
            borderRadius: '12px',
            textAlign: 'center',
            marginTop: '1rem'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🔍</div>
            <p style={{ fontSize: '1.1rem', color: '#92400e', margin: 0 }}>
              No high-confidence setups found. Try again later!
            </p>
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

