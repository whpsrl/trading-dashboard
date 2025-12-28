'use client';

import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function Home() {
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
