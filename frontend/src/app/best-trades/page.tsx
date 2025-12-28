'use client';

import BestTradesFinder from '@/components/BestTradesFinder';

export default function BestTradesPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0e13',
      padding: '2rem'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Page Header */}
        <div style={{
          marginBottom: '2rem',
          textAlign: 'center'
        }}>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: 'bold',
            marginBottom: '0.5rem',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            🎯 AI Best Trades Finder
          </h1>
          <p style={{
            fontSize: '1.1rem',
            color: '#888'
          }}>
            Find the best trading opportunities with AI-powered technical analysis
          </p>
        </div>

        {/* Info Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            background: '#0f1419',
            border: '1px solid #1e2329',
            borderRadius: '10px',
            padding: '1.5rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
              Multi-Indicator Analysis
            </div>
            <div style={{ fontSize: '0.85rem', color: '#888' }}>
              RSI, MACD, Bollinger Bands, Trend Analysis & more
            </div>
          </div>

          <div style={{
            background: '#0f1419',
            border: '1px solid #1e2329',
            borderRadius: '10px',
            padding: '1.5rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🤖</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
              AI Validation
            </div>
            <div style={{ fontSize: '0.85rem', color: '#888' }}>
              Claude AI validates setups and provides insights
            </div>
          </div>

          <div style={{
            background: '#0f1419',
            border: '1px solid #1e2329',
            borderRadius: '10px',
            padding: '1.5rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎯</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
              Smart Scoring
            </div>
            <div style={{ fontSize: '0.85rem', color: '#888' }}>
              0-100 score based on technical confluences
            </div>
          </div>

          <div style={{
            background: '#0f1419',
            border: '1px solid #1e2329',
            borderRadius: '10px',
            padding: '1.5rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📈</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
              Complete Trade Plan
            </div>
            <div style={{ fontSize: '0.85rem', color: '#888' }}>
              Entry, stop loss, targets with R:R ratios
            </div>
          </div>
        </div>

        {/* Main Component */}
        <BestTradesFinder apiUrl={apiUrl} />

        {/* How It Works */}
        <div style={{
          background: '#0f1419',
          border: '1px solid #1e2329',
          borderRadius: '12px',
          padding: '2rem',
          marginTop: '2rem'
        }}>
          <h3 style={{
            fontSize: '1.5rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            💡 How It Works
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem'
          }}>
            <div>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                marginBottom: '1rem'
              }}>
                1
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                Market Scan
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#888', lineHeight: '1.6' }}>
                Scans top cryptocurrencies and fetches OHLCV data from exchanges
              </p>
            </div>

            <div>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                marginBottom: '1rem'
              }}>
                2
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                Technical Analysis
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#888', lineHeight: '1.6' }}>
                Calculates 15+ technical indicators including RSI, MACD, Bollinger Bands, trend analysis
              </p>
            </div>

            <div>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                marginBottom: '1rem'
              }}>
                3
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                Smart Scoring
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#888', lineHeight: '1.6' }}>
                Multi-factor scoring system evaluates each setup based on technical confluences
              </p>
            </div>

            <div>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                marginBottom: '1rem'
              }}>
                4
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                AI Validation
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#888', lineHeight: '1.6' }}>
                High-scoring setups get validated by Claude AI for additional insights and risk assessment
              </p>
            </div>

            <div>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                marginBottom: '1rem'
              }}>
                5
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                Trade Planning
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#888', lineHeight: '1.6' }}>
                Automatically calculates entry, stop loss, and targets based on support/resistance and ATR
              </p>
            </div>

            <div>
              <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                marginBottom: '1rem'
              }}>
                6
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                Results
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#888', lineHeight: '1.6' }}>
                Get ranked opportunities with complete trade plans, confluences, and AI recommendations
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

