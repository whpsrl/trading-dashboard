'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [btcPrice, setBtcPrice] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchBTCPrice();
    // Update every 5 seconds
    const interval = setInterval(fetchBTCPrice, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchBTCPrice = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/market/price?symbol=BTC/USDT&exchange=binance`
      );
      const data = await response.json();
      setBtcPrice(data);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError('Failed to fetch price');
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(to bottom, #1a1a2e, #16213e)',
      color: 'white',
      padding: '2rem'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>
            📊 Trading Dashboard
          </h1>
          <p style={{ color: '#888', fontSize: '1.2rem' }}>
            AI-Powered Trading Intelligence Platform
          </p>
        </header>

        {/* Status Badge */}
        <div style={{ 
          textAlign: 'center', 
          marginBottom: '2rem',
          padding: '1rem',
          background: '#0f3460',
          borderRadius: '10px'
        }}>
          <span style={{ 
            background: '#00ff88', 
            color: '#000',
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            fontWeight: 'bold'
          }}>
            ✅ LIVE - Real Market Data
          </span>
        </div>

        {/* Main Price Display */}
        <div style={{
          background: '#0f3460',
          borderRadius: '20px',
          padding: '3rem',
          marginBottom: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
        }}>
          {loading && (
            <div style={{ textAlign: 'center', fontSize: '1.5rem' }}>
              Loading...
            </div>
          )}

          {error && (
            <div style={{ 
              textAlign: 'center', 
              color: '#ff6b6b',
              fontSize: '1.2rem'
            }}>
              ⚠️ {error}
              <br />
              <small style={{ color: '#888' }}>
                Make sure backend is running
              </small>
            </div>
          )}

          {btcPrice && !loading && (
            <div>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                gap: '1rem',
                marginBottom: '2rem'
              }}>
                <span style={{ fontSize: '2rem' }}>₿</span>
                <h2 style={{ fontSize: '2.5rem', margin: 0 }}>
                  BTC/USDT
                </h2>
              </div>

              <div style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '4rem', 
                  fontWeight: 'bold',
                  marginBottom: '1rem',
                  color: '#00ff88'
                }}>
                  ${btcPrice.price?.toLocaleString('en-US', { 
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2 
                  })}
                </div>

                <div style={{ 
                  fontSize: '1.5rem',
                  color: btcPrice.change_24h > 0 ? '#00ff88' : '#ff6b6b'
                }}>
                  {btcPrice.change_24h > 0 ? '↗' : '↘'} 
                  {' '}
                  {btcPrice.change_24h?.toFixed(2)}%
                  {' '}
                  (24h)
                </div>

                <div style={{ 
                  marginTop: '2rem',
                  padding: '1rem',
                  background: '#1a1a2e',
                  borderRadius: '10px',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '1rem'
                }}>
                  <div>
                    <div style={{ color: '#888', marginBottom: '0.5rem' }}>
                      Volume 24h
                    </div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold' }}>
                      ${(btcPrice.volume_24h / 1e9).toFixed(2)}B
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#888', marginBottom: '0.5rem' }}>
                      Exchange
                    </div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold' }}>
                      Binance
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginBottom: '3rem'
        }}>
          {[
            { icon: '🤖', title: 'AI Analysis', desc: 'Claude-powered insights' },
            { icon: '📈', title: 'Real-time Data', desc: 'Binance, OANDA, Finnhub' },
            { icon: '🎯', title: 'Custom Indicators', desc: 'Proprietary algorithms' },
            { icon: '⚡', title: 'Smart Alerts', desc: 'Multi-condition triggers' }
          ].map((feature, i) => (
            <div key={i} style={{
              background: '#0f3460',
              padding: '2rem',
              borderRadius: '15px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                {feature.icon}
              </div>
              <h3 style={{ marginBottom: '0.5rem' }}>{feature.title}</h3>
              <p style={{ color: '#888' }}>{feature.desc}</p>
            </div>
          ))}
        </div>

        {/* Footer */}
        <footer style={{ 
          textAlign: 'center', 
          color: '#888',
          paddingTop: '2rem',
          borderTop: '1px solid #333'
        }}>
          <p>🚀 Trading Dashboard v1.0 - Powered by Vercel + Railway</p>
          <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Real-time market data • AI-powered analysis • Professional trading tools
          </p>
        </footer>
      </div>
    </div>
  );
}
