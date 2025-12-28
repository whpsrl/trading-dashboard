'use client';

import { useState } from 'react';

interface TradeOpportunity {
  symbol: string;
  exchange: string;
  score: number;
  direction: 'LONG' | 'SHORT' | 'NEUTRAL';
  confidence: number;
  current_price: number;
  trade_levels: {
    entry: number;
    stop_loss: number;
    target_1: number;
    target_2: number;
    risk_reward_ratio_t1: number;
    risk_reward_ratio_t2: number;
    risk_percent: number;
  };
  confluences: string[];
  warnings: string[];
  recommendation: string;
  ai_insights?: any;
}

interface BestTradesDashboardProps {
  apiUrl: string;
}

export default function BestTradesDashboard({ apiUrl }: BestTradesDashboardProps) {
  const [opportunities, setOpportunities] = useState<TradeOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preset, setPreset] = useState<'quick' | 'balanced' | 'full'>('quick');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${apiUrl}/api/best-trades/scan?preset=${preset}&min_score=60`
      );
      const data = await response.json();
      
      if (data.success) {
        setOpportunities(data.opportunities);
      } else {
        setError('Failed to scan market');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scan market');
    } finally {
      setLoading(false);
    }
  };

  // Categorize opportunities
  const categorized = {
    crypto: opportunities.filter(o => o.symbol.includes('USDT') || o.symbol.includes('/')),
    stocks: opportunities.filter(o => 
      !o.symbol.includes('USDT') && 
      !['SPY', 'QQQ', 'DIA', 'IWM', 'VTI'].includes(o.symbol) &&
      !['GLD', 'SLV', 'USO', 'UNG'].includes(o.symbol) &&
      o.exchange !== 'forex'
    ),
    indices: opportunities.filter(o => ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI'].includes(o.symbol)),
    commodities: opportunities.filter(o => ['GLD', 'SLV', 'USO', 'UNG', 'CORN', 'WEAT'].includes(o.symbol)),
    forex: opportunities.filter(o => o.exchange === 'forex')
  };

  const categories = [
    { id: 'all', label: 'All Markets', emoji: '🌐', count: opportunities.length },
    { id: 'crypto', label: 'Crypto', emoji: '🪙', count: categorized.crypto.length },
    { id: 'stocks', label: 'Stocks', emoji: '📈', count: categorized.stocks.length },
    { id: 'indices', label: 'Indices', emoji: '📊', count: categorized.indices.length },
    { id: 'commodities', label: 'Commodities', emoji: '🥇', count: categorized.commodities.length },
    { id: 'forex', label: 'Forex', emoji: '💱', count: categorized.forex.length },
  ];

  const displayedOpportunities = selectedCategory === 'all' 
    ? opportunities 
    : categorized[selectedCategory as keyof typeof categorized] || [];

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#22c55e';
    if (score >= 70) return '#84cc16';
    if (score >= 60) return '#eab308';
    return '#ef4444';
  };

  const getDirectionColor = (direction: string) => {
    if (direction === 'LONG') return '#22c55e';
    if (direction === 'SHORT') return '#ef4444';
    return '#888';
  };

  return (
    <div style={{ background: '#0a0e13', minHeight: '100vh', padding: '2rem' }}>
      <div style={{ maxWidth: '1600px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{
            fontSize: '3rem',
            fontWeight: 'bold',
            marginBottom: '1rem',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🎯 AI Best Trades Finder
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#888' }}>
            Multi-Market Analysis Powered by Claude AI
          </p>
        </div>

        {/* Control Panel */}
        <div style={{
          background: '#0f1419',
          border: '1px solid #1e2329',
          borderRadius: '16px',
          padding: '2rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'flex',
            gap: '1.5rem',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {/* Preset Selection */}
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {['quick', 'balanced', 'full'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPreset(p as any)}
                  disabled={loading}
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '10px',
                    border: preset === p ? '2px solid #667eea' : '1px solid #2a2f35',
                    background: preset === p ? 'rgba(102, 126, 234, 0.1)' : '#1a1f25',
                    color: preset === p ? '#667eea' : '#888',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '0.95rem',
                    fontWeight: 'bold',
                    transition: 'all 0.2s',
                    textTransform: 'capitalize'
                  }}
                >
                  {p === 'quick' && '⚡'} {p === 'balanced' && '⚖️'} {p === 'full' && '🔥'} {p}
                </button>
              ))}
            </div>

            {/* Scan Button */}
            <button
              onClick={handleScan}
              disabled={loading}
              style={{
                padding: '0.75rem 2rem',
                borderRadius: '10px',
                background: loading
                  ? '#444'
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                transition: 'all 0.2s',
                transform: loading ? 'scale(1)' : 'scale(1)',
              }}
              onMouseOver={(e) => {
                if (!loading) e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              {loading ? '🔍 Scanning...' : '🚀 Start Scan'}
            </button>

            {/* Info */}
            {preset && !loading && (
              <div style={{
                fontSize: '0.85rem',
                color: '#888',
                textAlign: 'center'
              }}>
                {preset === 'quick' && '⚡ ~55 assets in 30s'}
                {preset === 'balanced' && '⚖️ ~80 assets in 60s'}
                {preset === 'full' && '🔥 ~150 assets in 2min'}
              </div>
            )}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div style={{
            textAlign: 'center',
            padding: '4rem',
            background: '#0f1419',
            borderRadius: '16px',
            marginBottom: '2rem'
          }}>
            <div style={{
              fontSize: '4rem',
              marginBottom: '1.5rem',
              animation: 'pulse 2s infinite'
            }}>
              🔍
            </div>
            <div style={{ fontSize: '1.3rem', color: '#fff', marginBottom: '0.5rem' }}>
              Scanning {preset} market...
            </div>
            <div style={{ fontSize: '1rem', color: '#888' }}>
              Analyzing crypto, stocks, forex, commodities & indices
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            background: '#3f1f1f',
            border: '2px solid #ef4444',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '2rem',
            textAlign: 'center',
            color: '#ef4444'
          }}>
            ❌ {error}
          </div>
        )}

        {/* Results */}
        {!loading && opportunities.length > 0 && (
          <>
            {/* Category Tabs */}
            <div style={{
              display: 'flex',
              gap: '1rem',
              marginBottom: '2rem',
              overflowX: 'auto',
              paddingBottom: '0.5rem'
            }}>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  style={{
                    padding: '1rem 1.5rem',
                    borderRadius: '12px',
                    border: selectedCategory === cat.id ? '2px solid #667eea' : '1px solid #2a2f35',
                    background: selectedCategory === cat.id 
                      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)'
                      : '#0f1419',
                    color: selectedCategory === cat.id ? '#fff' : '#888',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: 'bold',
                    transition: 'all 0.2s',
                    whiteSpace: 'nowrap',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <span style={{ fontSize: '1.3rem' }}>{cat.emoji}</span>
                  <span>{cat.label}</span>
                  <span style={{
                    background: selectedCategory === cat.id ? '#667eea' : '#2a2f35',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '20px',
                    fontSize: '0.85rem'
                  }}>
                    {cat.count}
                  </span>
                </button>
              ))}
            </div>

            {/* Opportunities Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
              gap: '1.5rem'
            }}>
              {displayedOpportunities.map((opp, idx) => (
                <div
                  key={idx}
                  style={{
                    background: '#0f1419',
                    border: `2px solid ${getScoreColor(opp.score)}`,
                    borderRadius: '16px',
                    padding: '1.5rem',
                    transition: 'all 0.3s',
                    cursor: 'pointer'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.boxShadow = `0 10px 30px ${getScoreColor(opp.score)}40`;
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  {/* Card Header */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '1rem',
                    paddingBottom: '1rem',
                    borderBottom: '1px solid #1e2329'
                  }}>
                    <div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                        {opp.symbol}
                      </div>
                      <div style={{ fontSize: '1.1rem', color: '#888' }}>
                        ${opp.current_price.toFixed(2)}
                      </div>
                    </div>

                    <div style={{
                      textAlign: 'right'
                    }}>
                      <div style={{
                        fontSize: '2.5rem',
                        fontWeight: 'bold',
                        color: getScoreColor(opp.score),
                        lineHeight: 1
                      }}>
                        {opp.score.toFixed(0)}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#888', marginTop: '0.25rem' }}>
                        SCORE
                      </div>
                    </div>
                  </div>

                  {/* Direction & Confidence */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      background: '#1a1f25',
                      padding: '0.75rem',
                      borderRadius: '8px'
                    }}>
                      <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.25rem' }}>
                        DIRECTION
                      </div>
                      <div style={{
                        fontSize: '1.2rem',
                        fontWeight: 'bold',
                        color: getDirectionColor(opp.direction)
                      }}>
                        {opp.direction === 'LONG' ? '📈' : '📉'} {opp.direction}
                      </div>
                    </div>

                    <div style={{
                      background: '#1a1f25',
                      padding: '0.75rem',
                      borderRadius: '8px'
                    }}>
                      <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.25rem' }}>
                        CONFIDENCE
                      </div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                        {opp.confidence.toFixed(0)}%
                      </div>
                    </div>
                  </div>

                  {/* Trade Levels */}
                  <div style={{
                    background: '#1a1f25',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1rem',
                    fontSize: '0.85rem'
                  }}>
                    <div style={{ color: '#888', marginBottom: '0.75rem', fontWeight: 'bold' }}>
                      📊 TRADE PLAN
                    </div>
                    <div style={{ display: 'grid', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#888' }}>Entry:</span>
                        <span style={{ color: '#00ff88' }}>${opp.trade_levels.entry.toFixed(2)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#888' }}>Stop Loss:</span>
                        <span style={{ color: '#ef4444' }}>${opp.trade_levels.stop_loss.toFixed(2)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#888' }}>Target 1:</span>
                        <span style={{ color: '#22c55e' }}>
                          ${opp.trade_levels.target_1.toFixed(2)} 
                          <span style={{ fontSize: '0.75rem', marginLeft: '0.25rem' }}>
                            (R:R {opp.trade_levels.risk_reward_ratio_t1.toFixed(1)}:1)
                          </span>
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: '#888' }}>Target 2:</span>
                        <span style={{ color: '#22c55e' }}>
                          ${opp.trade_levels.target_2.toFixed(2)}
                          <span style={{ fontSize: '0.75rem', marginLeft: '0.25rem' }}>
                            (R:R {opp.trade_levels.risk_reward_ratio_t2.toFixed(1)}:1)
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Confluences */}
                  {opp.confluences.length > 0 && (
                    <div style={{ fontSize: '0.8rem', color: '#22c55e' }}>
                      ✅ {opp.confluences.length} Confluences
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* No results in category */}
            {displayedOpportunities.length === 0 && selectedCategory !== 'all' && (
              <div style={{
                textAlign: 'center',
                padding: '3rem',
                background: '#0f1419',
                borderRadius: '16px',
                color: '#888'
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
                <div style={{ fontSize: '1.1rem' }}>
                  No opportunities found in {categories.find(c => c.id === selectedCategory)?.label}
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!loading && !error && opportunities.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '4rem',
            background: '#0f1419',
            borderRadius: '16px'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🎯</div>
            <div style={{ fontSize: '1.3rem', color: '#fff', marginBottom: '0.5rem' }}>
              Ready to Find Best Trades
            </div>
            <div style={{ fontSize: '1rem', color: '#888' }}>
              Select a preset and click "Start Scan" to analyze the market
            </div>
          </div>
        )}

      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}

