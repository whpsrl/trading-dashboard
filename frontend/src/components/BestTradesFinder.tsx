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
  ai_insights?: {
    valid: boolean;
    validation_score: number;
    risk_factors: string[];
    opportunities: string[];
    recommendation: string;
    caution: string;
  };
}

interface BestTradesFinderProps {
  apiUrl: string;
}

export default function BestTradesFinder({ apiUrl }: BestTradesFinderProps) {
  const [opportunities, setOpportunities] = useState<TradeOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanType, setScanType] = useState<'quick' | 'full'>('quick');
  const [minScore, setMinScore] = useState(60);

  const handleQuickScan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}/api/best-trades/top?limit=5&timeframe=1h`);
      const data = await response.json();
      
      if (data.success) {
        setOpportunities(data.opportunities);
      } else {
        setError('Failed to fetch opportunities');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scan market');
    } finally {
      setLoading(false);
    }
  };

  const handleFullScan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${apiUrl}/api/best-trades/scan?min_score=${minScore}&timeframe=1h`
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

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#22c55e'; // green
    if (score >= 70) return '#84cc16'; // lime
    if (score >= 60) return '#eab308'; // yellow
    return '#ef4444'; // red
  };

  const getDirectionColor = (direction: string) => {
    if (direction === 'LONG') return '#22c55e';
    if (direction === 'SHORT') return '#ef4444';
    return '#888';
  };

  return (
    <div style={{
      background: '#0f1419',
      border: '1px solid #1e2329',
      borderRadius: '12px',
      padding: '2rem',
      marginBottom: '2rem'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ 
          fontSize: '1.8rem', 
          marginBottom: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          🎯 Best Trades Finder
        </h2>
        <p style={{ color: '#888', fontSize: '0.95rem' }}>
          AI-powered analysis to find the best trading opportunities
        </p>
      </div>

      {/* Controls */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <button
          onClick={handleQuickScan}
          disabled={loading}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            opacity: loading ? 0.6 : 1,
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            if (!loading) e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          ⚡ Quick Scan (Top 20)
        </button>

        <button
          onClick={handleFullScan}
          disabled={loading}
          style={{
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            opacity: loading ? 0.6 : 1,
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            if (!loading) e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          🔥 Full Scan (Top 30)
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label style={{ color: '#888', fontSize: '0.9rem' }}>Min Score:</label>
          <input
            type="number"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            min={0}
            max={100}
            style={{
              background: '#1a1f25',
              border: '1px solid #2a2f35',
              borderRadius: '6px',
              padding: '0.5rem',
              color: 'white',
              width: '80px',
              fontSize: '0.9rem'
            }}
          />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          color: '#888'
        }}>
          <div style={{
            fontSize: '3rem',
            marginBottom: '1rem',
            animation: 'pulse 2s infinite'
          }}>
            🔍
          </div>
          <div style={{ fontSize: '1.1rem' }}>
            Scanning market for best opportunities...
          </div>
          <div style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
            This may take a minute...
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div style={{
          background: '#3f1f1f',
          border: '1px solid #ef4444',
          borderRadius: '8px',
          padding: '1rem',
          color: '#ef4444',
          marginBottom: '1rem'
        }}>
          ❌ {error}
        </div>
      )}

      {/* Opportunities List */}
      {!loading && opportunities.length > 0 && (
        <div>
          <div style={{
            fontSize: '1.2rem',
            fontWeight: 'bold',
            marginBottom: '1.5rem',
            color: '#00ff88'
          }}>
            🎯 Found {opportunities.length} Trading Opportunities
          </div>

          <div style={{
            display: 'grid',
            gap: '1.5rem'
          }}>
            {opportunities.map((opp, idx) => (
              <div
                key={idx}
                style={{
                  background: '#1a1f25',
                  border: '2px solid ' + getScoreColor(opp.score),
                  borderRadius: '12px',
                  padding: '1.5rem',
                  transition: 'transform 0.2s'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                {/* Header Row */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '1rem',
                  paddingBottom: '1rem',
                  borderBottom: '1px solid #2a2f35'
                }}>
                  <div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {opp.symbol}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#888' }}>
                      ${opp.current_price.toFixed(2)}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{
                      fontSize: '2rem',
                      fontWeight: 'bold',
                      color: getScoreColor(opp.score)
                    }}>
                      {opp.score.toFixed(0)}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#888' }}>
                      Score
                    </div>
                  </div>
                </div>

                {/* Direction & Confidence */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '1rem',
                  marginBottom: '1rem'
                }}>
                  <div>
                    <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '0.25rem' }}>
                      Direction
                    </div>
                    <div style={{
                      fontSize: '1.3rem',
                      fontWeight: 'bold',
                      color: getDirectionColor(opp.direction)
                    }}>
                      {opp.direction === 'LONG' ? '📈' : '📉'} {opp.direction}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '0.25rem' }}>
                      Confidence
                    </div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 'bold' }}>
                      {opp.confidence.toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Trade Levels */}
                <div style={{
                  background: '#0f1419',
                  borderRadius: '8px',
                  padding: '1rem',
                  marginBottom: '1rem'
                }}>
                  <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.75rem' }}>
                    📊 Trade Plan
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '0.75rem',
                    fontSize: '0.9rem'
                  }}>
                    <div>
                      <span style={{ color: '#888' }}>Entry:</span>{' '}
                      <span style={{ color: '#00ff88' }}>${opp.trade_levels.entry.toFixed(2)}</span>
                    </div>
                    <div>
                      <span style={{ color: '#888' }}>Stop Loss:</span>{' '}
                      <span style={{ color: '#ef4444' }}>${opp.trade_levels.stop_loss.toFixed(2)}</span>
                    </div>
                    <div>
                      <span style={{ color: '#888' }}>Target 1:</span>{' '}
                      <span style={{ color: '#22c55e' }}>${opp.trade_levels.target_1.toFixed(2)}</span>
                      <span style={{ color: '#888', fontSize: '0.8rem', marginLeft: '0.25rem' }}>
                        (R:R {opp.trade_levels.risk_reward_ratio_t1.toFixed(1)}:1)
                      </span>
                    </div>
                    <div>
                      <span style={{ color: '#888' }}>Target 2:</span>{' '}
                      <span style={{ color: '#22c55e' }}>${opp.trade_levels.target_2.toFixed(2)}</span>
                      <span style={{ color: '#888', fontSize: '0.8rem', marginLeft: '0.25rem' }}>
                        (R:R {opp.trade_levels.risk_reward_ratio_t2.toFixed(1)}:1)
                      </span>
                    </div>
                  </div>
                </div>

                {/* Confluences */}
                {opp.confluences.length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>
                      ✅ Confluences ({opp.confluences.length})
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#22c55e' }}>
                      {opp.confluences.map((conf, i) => (
                        <div key={i} style={{ marginBottom: '0.25rem' }}>
                          • {conf}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {opp.warnings.length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>
                      ⚠️ Warnings
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#eab308' }}>
                      {opp.warnings.map((warn, i) => (
                        <div key={i} style={{ marginBottom: '0.25rem' }}>
                          • {warn}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Insights */}
                {opp.ai_insights && (
                  <div style={{
                    background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.5rem' }}>
                      🤖 AI Validation (Score: {opp.ai_insights.validation_score}/10)
                    </div>
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                      {opp.ai_insights.recommendation}
                    </div>
                  </div>
                )}

                {/* Recommendation */}
                <div style={{
                  fontSize: '0.95rem',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                  color: '#ddd'
                }}>
                  {opp.recommendation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && opportunities.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          color: '#888'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
          <div style={{ fontSize: '1.1rem' }}>
            Click a scan button to find trading opportunities
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        background: '#1a1f25',
        borderRadius: '8px',
        fontSize: '0.8rem',
        color: '#888',
        textAlign: 'center'
      }}>
        ⚠️ This is AI-powered analysis for educational purposes only. Not financial advice.
        Always do your own research and manage risk appropriately.
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}

