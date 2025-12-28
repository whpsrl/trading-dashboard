'use client';

import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { useState } from 'react';

export default function Home() {
  const [assetRequest, setAssetRequest] = useState('');
  const [timeframe, setTimeframe] = useState('1h');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!assetRequest.trim()) {
      alert('Inserisci un asset da analizzare');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://trading-dashboard-production-79d9.up.railway.app';
      const response = await fetch(`${apiUrl}/api/best-trades/analyze/${assetRequest}?timeframe=${timeframe}`);
      
      if (!response.ok) {
        throw new Error('Analisi fallita');
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Errore nell\'analisi. Controlla il simbolo asset.');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      title: '🎯 Best Trades Finder',
      description: 'AI-powered multi-market scanner finds the best trading opportunities',
      link: '/best-trades',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      features: [
        '150+ assets scanned',
        'Crypto, Stocks, Forex, Commodities',
        'AI validation with Claude',
        'Complete trade plans'
      ]
    },
    {
      title: '📊 Chart Analyzer',
      description: 'Analyze crypto charts with AI-powered technical analysis',
      link: '/chart',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      features: [
        'Real-time crypto charts',
        'AI pattern recognition',
        'Support/Resistance auto-draw',
        'Technical indicators'
      ]
    },
    {
      title: '🔍 Market Scanner',
      description: 'Full market scan with AI analysis for all assets',
      link: '/scanner',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      features: [
        'Real-time scanning',
        'Multiple timeframes',
        'Smart filtering',
        'Telegram notifications'
      ]
    },
    {
      title: '📈 Stock Analyzer',
      description: 'Analyze stocks, ETFs and indices with advanced tools',
      link: '/stocks',
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      features: [
        'US stocks & indices',
        'Technical analysis',
        'AI insights',
        'Price alerts'
      ]
    }
  ];

  return (
    <>
      <Navbar />
      
      <main style={{
        background: '#0a0e13',
        minHeight: 'calc(100vh - 80px)',
        padding: '4rem 2rem'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          
          {/* Hero Section */}
          <div style={{
            textAlign: 'center',
            marginBottom: '4rem'
          }}>
            <h1 style={{
              fontSize: '4rem',
              fontWeight: 'bold',
              marginBottom: '1.5rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: 1.2
            }}>
              AI Trading Dashboard
            </h1>
            <p style={{
              fontSize: '1.5rem',
              color: '#888',
              marginBottom: '2rem',
              maxWidth: '800px',
              margin: '0 auto'
            }}>
              Multi-market analysis powered by Claude AI.<br />
              Find the best trading opportunities across crypto, stocks, forex & more.
            </p>

            {/* Quick Stats */}
            <div style={{
              display: 'flex',
              gap: '2rem',
              justifyContent: 'center',
              marginTop: '3rem',
              flexWrap: 'wrap'
            }}>
              {[
                { label: 'Markets', value: '5+', emoji: '🌐' },
                { label: 'Assets', value: '150+', emoji: '📊' },
                { label: 'Indicators', value: '15+', emoji: '📈' },
                { label: 'AI Score', value: '0-100', emoji: '🤖' }
              ].map((stat, idx) => (
                <div key={idx} style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '16px',
                  padding: '1.5rem 2rem',
                  minWidth: '140px'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                    {stat.emoji}
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    {stat.value}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#888' }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Features Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '2rem',
            marginBottom: '4rem'
          }}>
            {features.map((feature, idx) => (
              <Link
                key={idx}
                href={feature.link}
                style={{
                  background: '#0f1419',
                  border: '2px solid transparent',
                  borderRadius: '20px',
                  padding: '2rem',
                  textDecoration: 'none',
                  color: 'white',
                  transition: 'all 0.3s',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.borderImage = `${feature.gradient} 1`;
                  e.currentTarget.style.boxShadow = '0 20px 40px rgba(102, 126, 234, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderImage = 'none';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {/* Gradient Background */}
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: feature.gradient
                }} />

                <h3 style={{
                  fontSize: '1.8rem',
                  marginBottom: '1rem',
                  fontWeight: 'bold'
                }}>
                  {feature.title}
                </h3>

                <p style={{
                  fontSize: '1rem',
                  color: '#888',
                  marginBottom: '1.5rem',
                  lineHeight: 1.6
                }}>
                  {feature.description}
                </p>

                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem'
                }}>
                  {feature.features.map((item, i) => (
                    <li key={i} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      fontSize: '0.9rem',
                      color: '#aaa'
                    }}>
                      <span style={{
                        color: '#22c55e',
                        fontSize: '1.2rem'
                      }}>✓</span>
                      {item}
                    </li>
                  ))}
                </ul>

                <div style={{
                  marginTop: '1.5rem',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '10px',
                  background: feature.gradient,
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '1rem'
                }}>
                  Launch →
                </div>
              </Link>
            ))}
          </div>

          {/* Custom Asset Analysis Request */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
            border: '2px solid rgba(102, 126, 234, 0.3)',
            borderRadius: '20px',
            padding: '3rem',
            marginBottom: '4rem'
          }}>
            <h2 style={{
              fontSize: '2rem',
              marginBottom: '1rem',
              fontWeight: 'bold',
              textAlign: 'center'
            }}>
              🎯 Richiedi Analisi Personalizzata
            </h2>
            <p style={{
              fontSize: '1.1rem',
              color: '#aaa',
              textAlign: 'center',
              marginBottom: '2rem'
            }}>
              Inserisci qualsiasi asset (es: BTC/USDT, AAPL, EUR_USD, GOLD) per un'analisi AI approfondita
            </p>

            <div style={{
              maxWidth: '600px',
              margin: '0 auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '1.5rem'
            }}>
              <div style={{
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap'
              }}>
                <input
                  type="text"
                  placeholder="Es: BTC/USDT, AAPL, EUR_USD, GOLD..."
                  value={assetRequest}
                  onChange={(e) => setAssetRequest(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                  style={{
                    flex: '1',
                    minWidth: '250px',
                    padding: '1rem 1.5rem',
                    fontSize: '1.1rem',
                    borderRadius: '12px',
                    border: '2px solid rgba(102, 126, 234, 0.3)',
                    background: 'rgba(0, 0, 0, 0.3)',
                    color: 'white',
                    outline: 'none'
                  }}
                />

                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  style={{
                    padding: '1rem 1.5rem',
                    fontSize: '1.1rem',
                    borderRadius: '12px',
                    border: '2px solid rgba(102, 126, 234, 0.3)',
                    background: 'rgba(0, 0, 0, 0.3)',
                    color: 'white',
                    outline: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <option value="15m">15 min</option>
                  <option value="1h">1 ora</option>
                  <option value="4h">4 ore</option>
                  <option value="1d">1 giorno</option>
                </select>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={loading}
                style={{
                  padding: '1rem 2rem',
                  fontSize: '1.2rem',
                  fontWeight: 'bold',
                  borderRadius: '12px',
                  border: 'none',
                  background: loading 
                    ? 'rgba(102, 126, 234, 0.5)' 
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.3s',
                  opacity: loading ? 0.7 : 1
                }}
              >
                {loading ? '🔄 Analizzando...' : '🚀 Analizza con AI'}
              </button>
            </div>

            {/* Result Display */}
            {result && (
              <div style={{
                marginTop: '2rem',
                padding: '2rem',
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '12px',
                border: '1px solid rgba(102, 126, 234, 0.2)'
              }}>
                <h3 style={{
                  fontSize: '1.5rem',
                  marginBottom: '1rem',
                  color: '#fff'
                }}>
                  📊 {result.symbol} - Analisi Completa
                </h3>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '1rem',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{
                    background: 'rgba(102, 126, 234, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Score</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#fff' }}>
                      {result.score_data?.total_score?.toFixed(1)}/100
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(102, 126, 234, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Direzione</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fff' }}>
                      {result.score_data?.direction === 'LONG' ? '🟢 LONG' : result.score_data?.direction === 'SHORT' ? '🔴 SHORT' : '⚪ NEUTRAL'}
                    </div>
                  </div>

                  <div style={{
                    background: 'rgba(102, 126, 234, 0.1)',
                    padding: '1rem',
                    borderRadius: '8px'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>Prezzo</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fff' }}>
                      ${result.indicators?.current_price?.toFixed(2)}
                    </div>
                  </div>
                </div>

                {result.ai_validation && (
                  <div style={{
                    background: 'rgba(102, 126, 234, 0.05)',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    marginTop: '1rem'
                  }}>
                    <h4 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#667eea' }}>
                      🤖 Analisi AI
                    </h4>
                    <p style={{ color: '#ddd', lineHeight: 1.6, marginBottom: '1rem' }}>
                      {result.ai_validation.recommendation}
                    </p>
                    {result.ai_validation.caution && (
                      <p style={{ color: '#ff6b6b', lineHeight: 1.6 }}>
                        ⚠️ {result.ai_validation.caution}
                      </p>
                    )}
                  </div>
                )}

                <Link
                  href={`/best-trades`}
                  style={{
                    display: 'inline-block',
                    marginTop: '1rem',
                    padding: '0.75rem 1.5rem',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                >
                  Vedi Dashboard Completa →
                </Link>
              </div>
            )}
          </div>

          {/* Info Section */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
            border: '1px solid rgba(102, 126, 234, 0.3)',
            borderRadius: '20px',
            padding: '3rem',
            textAlign: 'center'
          }}>
            <h2 style={{
              fontSize: '2rem',
              marginBottom: '1rem',
              fontWeight: 'bold'
            }}>
              🤖 Powered by Claude AI
            </h2>
            <p style={{
              fontSize: '1.1rem',
              color: '#aaa',
              maxWidth: '800px',
              margin: '0 auto',
              lineHeight: 1.6
            }}>
              Advanced technical analysis with 15+ indicators including RSI, MACD, Bollinger Bands, 
              trend analysis, volume profiling, and support/resistance detection. 
              All validated by Claude Sonnet 4 for maximum accuracy.
            </p>

            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'center',
              marginTop: '2rem',
              flexWrap: 'wrap'
            }}>
              <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '1rem 1.5rem',
                borderRadius: '10px',
                fontSize: '0.9rem'
              }}>
                🪙 Binance (Real-time)
              </div>
              <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '1rem 1.5rem',
                borderRadius: '10px',
                fontSize: '0.9rem'
              }}>
                📈 Finnhub (Real-time)
              </div>
              <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '1rem 1.5rem',
                borderRadius: '10px',
                fontSize: '0.9rem'
              }}>
                💱 OANDA (Real-time)
              </div>
              <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '1rem 1.5rem',
                borderRadius: '10px',
                fontSize: '0.9rem'
              }}>
                📱 Telegram Bot
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
