'use client'

import { useState } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function CommoditiesPage() {
  const [scanning, setScanning] = useState(false)
  const [message, setMessage] = useState('')
  const [results, setResults] = useState<any[] | null>(null)
  const [aiProvider, setAiProvider] = useState('claude')
  const [timeframe, setTimeframe] = useState('4h')

  const timeframes = [
    { value: '15m', label: '15 Minutes', emoji: '⚡' },
    { value: '1h', label: '1 Hour', emoji: '⏰' },
    { value: '4h', label: '4 Hours', emoji: '📊' }
  ]

  const commodities = [
    { name: 'Gold Futures', symbol: 'GC=F', emoji: '🥇', description: 'Precious metal, safe haven asset' },
    { name: 'Crude Oil WTI', symbol: 'CL=F', emoji: '🛢️', description: 'Energy commodity, global benchmark' },
    { name: 'Silver Futures', symbol: 'SI=F', emoji: '🥈', description: 'Precious metal, industrial use' },
  ]

  const runScan = async () => {
    setScanning(true)
    setMessage(`🥇 Scanning commodities on ${timeframe.toUpperCase()} with ${aiProvider.toUpperCase()} AI...`)
    setResults(null)

    try {
      const url = `${BACKEND_URL}/api/commodities/scan?ai_provider=${aiProvider}&timeframe=${timeframe}`
      console.log('🚀 Calling:', url)
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      console.log('📡 Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ Error response:', errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('✅ Response data:', data)

      if (data.success) {
        setMessage(`✅ Scan complete! Found ${data.count} commodity setups. Check Telegram for alerts.`)
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
      setMessage('❌ Failed to scan commodities: ' + (error as Error).message)
    } finally {
      setScanning(false)
    }
  }

  return (
    <div style={{
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '0 1.5rem'
    }}>
      <h1 style={{
        fontSize: '2.5rem',
        fontWeight: 'bold',
        marginBottom: '1rem',
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        🥇 Commodities Scanner
      </h1>

      <p style={{
        fontSize: '1.1rem',
        color: '#666',
        marginBottom: '2rem',
        lineHeight: '1.6'
      }}>
        AI-powered analysis of major commodity futures on <strong>15M, 1H, and 4H timeframes</strong>.
        <br/>
        <span style={{ fontSize: '0.95rem', color: '#999' }}>
          ⏰ Data from Yahoo Finance (15-20 min delay) | Auto-scan runs on 4H every 4h (+30min after candle close)
        </span>
      </p>

      {/* Commodities Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        {commodities.map((commodity) => (
          <div key={commodity.symbol} style={{
            background: 'white',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
            borderTop: '4px solid #f59e0b',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>{commodity.emoji}</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#333' }}>
              {commodity.name}
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.25rem' }}>
              {commodity.symbol}
            </p>
            <p style={{ fontSize: '0.8rem', color: '#999' }}>
              {commodity.description}
            </p>
          </div>
        ))}
      </div>

      {/* Settings */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
        marginBottom: '2rem'
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem', color: '#333' }}>
          ⚙️ Scan Settings
        </h2>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            fontSize: '0.9rem',
            fontWeight: '600',
            color: '#555',
            marginBottom: '0.5rem'
          }}>
            📊 Timeframe
          </label>
          <select 
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              borderRadius: '8px',
              border: '2px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer',
              marginBottom: '1rem'
            }}
          >
            <option value="15m">⚡ 15 Minutes (Scalping)</option>
            <option value="1h">⏰ 1 Hour (Intraday)</option>
            <option value="4h">📊 4 Hours (Swing - default)</option>
          </select>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            fontSize: '0.9rem',
            fontWeight: '600',
            color: '#555',
            marginBottom: '0.5rem'
          }}>
            🤖 AI Provider
          </label>
          <select 
            value={aiProvider}
            onChange={(e) => setAiProvider(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              borderRadius: '8px',
              border: '2px solid #e5e7eb',
              backgroundColor: 'white',
              cursor: 'pointer'
            }}
          >
            <option value="claude">Claude Sonnet 4 (default)</option>
            <option value="groq">Groq (Llama 3.3 - FAST!)</option>
          </select>
        </div>

        <button
          onClick={runScan}
          disabled={scanning}
          style={{
            width: '100%',
            padding: '1rem',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            borderRadius: '12px',
            border: 'none',
            background: scanning 
              ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'
              : 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            color: 'white',
            cursor: scanning ? 'not-allowed' : 'pointer',
            transition: 'transform 0.2s, box-shadow 0.2s',
            boxShadow: '0 4px 15px rgba(245, 158, 11, 0.3)'
          }}
          onMouseEnter={(e) => {
            if (!scanning) {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(245, 158, 11, 0.4)'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 4px 15px rgba(245, 158, 11, 0.3)'
          }}
        >
          {scanning ? '🔄 Scanning...' : `🚀 Scan Commodities (${timeframe.toUpperCase()})`}
        </button>

        {message && (
          <div style={{
            marginTop: '1.5rem',
            padding: '1rem',
            borderRadius: '8px',
            background: message.includes('❌') ? '#fee2e2' : message.includes('✅') ? '#d1fae5' : '#fef3c7',
            color: message.includes('❌') ? '#991b1b' : message.includes('✅') ? '#065f46' : '#92400e',
            fontSize: '0.95rem',
            fontWeight: '500'
          }}>
            {message}
          </div>
        )}
      </div>

      {/* Results Display */}
      {results && results.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '1.5rem', color: '#333' }}>
            📊 Scan Results ({results.length} Setups)
          </h2>
          <div style={{ display: 'grid', gap: '1.5rem', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
            {results.map((setup, index) => (
              <div key={index} style={{
                background: 'white',
                borderRadius: '12px',
                padding: '1.5rem',
                boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
                borderLeft: `5px solid ${setup.direction === 'LONG' ? '#10b981' : setup.direction === 'SHORT' ? '#ef4444' : '#9ca3af'}`
              }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#333' }}>
                  {setup.symbol} <span style={{ fontSize: '0.9rem', color: '#666' }}>({setup.timeframe})</span>
                </h3>
                <p style={{ marginBottom: '0.25rem', color: '#444' }}>
                  Direction: <span style={{ fontWeight: '600', color: setup.direction === 'LONG' ? '#10b981' : setup.direction === 'SHORT' ? '#ef4444' : '#666' }}>{setup.direction}</span>
                </p>
                <p style={{ marginBottom: '0.25rem', color: '#444' }}>Confidence: <span style={{ fontWeight: '600' }}>{setup.confidence}%</span></p>
                <p style={{ marginBottom: '0.25rem', color: '#444' }}>AI: <span style={{ fontWeight: '600' }}>{setup.ai_provider?.toUpperCase()}</span></p>
                <p style={{ marginTop: '1rem', color: '#555', fontSize: '0.95rem', lineHeight: '1.5' }}>
                  <strong>Entry:</strong> ${setup.entry?.toFixed(2)} | 
                  <strong> TP:</strong> ${setup.take_profit?.toFixed(2)} | 
                  <strong> SL:</strong> ${setup.stop_loss?.toFixed(2)}
                </p>
                <p style={{ marginTop: '1rem', color: '#555', fontSize: '0.9rem', fontStyle: 'italic' }}>
                  "{setup.reasoning}"
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Section */}
      <div style={{
        marginTop: '3rem',
        padding: '1.5rem',
        background: '#fffbeb',
        borderRadius: '12px',
        border: '1px solid #fcd34d'
      }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem', color: '#92400e' }}>
          ℹ️ How Auto-Scan Works
        </h3>
        <ul style={{ listStyle: 'none', display: 'grid', gap: '0.75rem', paddingLeft: 0, color: '#78350f', fontSize: '0.95rem' }}>
          <li>📊 <strong>Manual Scan</strong>: Choose 15m, 1h, or 4h timeframe</li>
          <li>⏰ <strong>Auto-scan (4H only)</strong>: Every 4 hours at 04:30, 08:30, 12:30, 16:30, 20:30, 00:30 UTC</li>
          <li>🥇 <strong>3 Commodities</strong>: Gold, Crude Oil, Silver (Yahoo Finance data)</li>
          <li>⏳ <strong>+30 min delay</strong>: Ensures complete data availability after candle close</li>
          <li>🤖 <strong>AI Analysis</strong>: Claude/Groq analyzes 100 candles</li>
          <li>📱 <strong>Telegram Alerts</strong>: Automatic notifications for high-confidence setups</li>
          <li>🔄 <strong>Trade Tracking</strong>: Monitors TP/SL, updates performance stats</li>
        </ul>
      </div>
    </div>
  )
}
