'use client'

import Link from 'next/link'

export default function Home() {
  return (
    <div style={{
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '0 1.5rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '4rem 3rem',
        boxShadow: '0 25px 70px rgba(0,0,0,0.2)',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}>
          🤖
        </div>
        
        <h1 style={{
          fontSize: '3rem',
          fontWeight: 'bold',
          marginBottom: '1rem',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          AI Trading Bot
        </h1>

        <p style={{
          fontSize: '1.25rem',
          color: '#666',
          marginBottom: '3rem',
          maxWidth: '600px',
          margin: '0 auto 3rem'
        }}>
          Powered by <strong>Claude Sonnet 4</strong> for intelligent market analysis
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginBottom: '3rem'
        }}>
          <Link href="/crypto" style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '2rem',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              boxShadow: '0 10px 25px rgba(102, 126, 234, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>₿</div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Crypto</h3>
              <p style={{ fontSize: '0.95rem', opacity: 0.9 }}>Top 15 pairs • 3 Timeframes</p>
            </div>
          </Link>

          <Link href="/indices" style={{ textDecoration: 'none' }}>
            <div style={{
              background: '#e5e7eb',
              color: '#6b7280',
              padding: '2rem',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📊</div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Indices</h3>
              <p style={{ fontSize: '0.95rem' }}>Coming Soon...</p>
            </div>
          </Link>

          <Link href="/stocks" style={{ textDecoration: 'none' }}>
            <div style={{
              background: '#e5e7eb',
              color: '#6b7280',
              padding: '2rem',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📈</div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Stocks</h3>
              <p style={{ fontSize: '0.95rem' }}>Coming Soon...</p>
            </div>
          </Link>

          <Link href="/commodities" style={{ textDecoration: 'none' }}>
            <div style={{
              background: '#e5e7eb',
              color: '#6b7280',
              padding: '2rem',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🪙</div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Commodities</h3>
              <p style={{ fontSize: '0.95rem' }}>Coming Soon...</p>
            </div>
          </Link>

          <Link href="/forex" style={{ textDecoration: 'none' }}>
            <div style={{
              background: '#e5e7eb',
              color: '#6b7280',
              padding: '2rem',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-5px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>💱</div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Forex</h3>
              <p style={{ fontSize: '0.95rem' }}>Coming Soon...</p>
            </div>
          </Link>
        </div>

        <div style={{
          padding: '2rem',
          background: '#f9fafb',
          borderRadius: '12px',
          textAlign: 'left'
        }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '1rem', fontSize: '1.25rem' }}>✨ Features:</h3>
          <ul style={{ listStyle: 'none', display: 'grid', gap: '0.75rem', paddingLeft: 0 }}>
            <li>🧠 <strong>AI-Powered Analysis</strong> - Claude Sonnet 4 deep market insights</li>
            <li>📊 <strong>Multi-Timeframe</strong> - 15m, 1h, 4h coverage</li>
            <li>📱 <strong>Telegram Alerts</strong> - Entry, TP, SL + reasoning</li>
            <li>🔄 <strong>Auto-Scan</strong> - Top pairs by volume</li>
            <li>⚡ <strong>Real-Time</strong> - Live Binance data</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

