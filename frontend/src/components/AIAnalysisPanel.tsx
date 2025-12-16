'use client';

import { useEffect, useState } from 'react';

interface AIAnalysis {
  available: boolean;
  sentiment?: string;
  confidence?: number;
  trend?: string;
  signals?: Array<{
    type: string;
    strength: string;
    reason: string;
  }>;
  technical_analysis?: string;
  risk_level?: string;
  key_points?: string[];
  recommendation?: string;
  message?: string;
  error?: string;
}

interface AIAnalysisPanelProps {
  symbol: string;
  assetType: string;
  apiUrl: string;
}

export default function AIAnalysisPanel({ symbol, assetType, apiUrl }: AIAnalysisPanelProps) {
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchAnalysis();
    // Update every 5 minutes
    const interval = setInterval(fetchAnalysis, 300000);
    return () => clearInterval(interval);
  }, [symbol, assetType]);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${apiUrl}/api/ai/analyze?symbol=${symbol}&asset_type=${assetType}&timeframe=1h`
      );
      const data = await response.json();
      
      if (data.available && data.analysis) {
        setAnalysis({
          available: true,
          ...data.analysis
        });
      } else {
        setAnalysis(data);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('AI Analysis error:', err);
      setAnalysis({
        available: false,
        message: 'Failed to fetch AI analysis'
      });
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'bullish': return '#26a69a';
      case 'bearish': return '#ef5350';
      default: return '#888';
    }
  };

  const getRiskColor = (risk?: string) => {
    switch (risk?.toLowerCase()) {
      case 'low': return '#26a69a';
      case 'medium': return '#ff9800';
      case 'high': return '#ef5350';
      default: return '#888';
    }
  };

  const getSignalIcon = (type?: string) => {
    switch (type?.toUpperCase()) {
      case 'BUY': return '🟢';
      case 'SELL': return '🔴';
      case 'HOLD': return '🟡';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div style={{
        background: '#0f1419',
        border: '1px solid #1e2329',
        borderRadius: '10px',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🤖</div>
        <div style={{ color: '#888' }}>Analyzing {symbol}...</div>
      </div>
    );
  }

  if (!analysis?.available) {
    return (
      <div style={{
        background: '#0f1419',
        border: '1px solid #1e2329',
        borderRadius: '10px',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🤖</div>
        <div style={{ color: '#888', marginBottom: '0.5rem' }}>
          AI Analysis Unavailable
        </div>
        <div style={{ fontSize: '0.9rem', color: '#666' }}>
          {analysis?.message || 'Configure ANTHROPIC_API_KEY to enable'}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: '#0f1419',
      border: '1px solid #1e2329',
      borderRadius: '10px',
      overflow: 'hidden',
      marginBottom: '2rem'
    }}>
      {/* Header */}
      <div style={{
        padding: '1.5rem',
        borderBottom: '1px solid #1e2329',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🤖</span>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem' }}>AI Analysis</h3>
            <div style={{ fontSize: '0.8rem', color: '#888' }}>
              Powered by Claude Sonnet 4
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#00ff88',
            cursor: 'pointer',
            fontSize: '0.9rem',
            padding: '0.5rem'
          }}
        >
          {expanded ? '▼ Less' : '▶ More'}
        </button>
      </div>

      {/* Quick Summary */}
      <div style={{
        padding: '1.5rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '1rem'
      }}>
        {/* Sentiment */}
        <div>
          <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '0.5rem' }}>
            Sentiment
          </div>
          <div style={{
            fontSize: '1.3rem',
            fontWeight: 'bold',
            color: getSentimentColor(analysis.sentiment)
          }}>
            {analysis.sentiment || 'N/A'}
            {analysis.confidence && (
              <span style={{ fontSize: '0.8rem', marginLeft: '0.5rem', color: '#888' }}>
                ({analysis.confidence}%)
              </span>
            )}
          </div>
        </div>

        {/* Trend */}
        <div>
          <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '0.5rem' }}>
            Trend
          </div>
          <div style={{
            fontSize: '1.1rem',
            fontWeight: 'bold'
          }}>
            {analysis.trend || 'N/A'}
          </div>
        </div>

        {/* Risk */}
        <div>
          <div style={{ fontSize: '0.85rem', color: '#888', marginBottom: '0.5rem' }}>
            Risk Level
          </div>
          <div style={{
            fontSize: '1.3rem',
            fontWeight: 'bold',
            color: getRiskColor(analysis.risk_level)
          }}>
            {analysis.risk_level || 'N/A'}
          </div>
        </div>
      </div>

      {/* Signals */}
      {analysis.signals && analysis.signals.length > 0 && (
        <div style={{
          padding: '1.5rem',
          borderTop: '1px solid #1e2329'
        }}>
          <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '1rem' }}>
            Trading Signals
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {analysis.signals.map((signal, idx) => (
              <div key={idx} style={{
                background: '#1a1f25',
                padding: '0.75rem',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem'
              }}>
                <span style={{ fontSize: '1.2rem' }}>{getSignalIcon(signal.type)}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    {signal.type} - {signal.strength}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#888' }}>
                    {signal.reason}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expanded Details */}
      {expanded && (
        <>
          {/* Key Points */}
          {analysis.key_points && analysis.key_points.length > 0 && (
            <div style={{
              padding: '1.5rem',
              borderTop: '1px solid #1e2329'
            }}>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '1rem' }}>
                Key Points
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#ddd' }}>
                {analysis.key_points.map((point, idx) => (
                  <li key={idx} style={{ marginBottom: '0.5rem' }}>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Technical Analysis */}
          {analysis.technical_analysis && (
            <div style={{
              padding: '1.5rem',
              borderTop: '1px solid #1e2329'
            }}>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '1rem' }}>
                Technical Analysis
              </div>
              <div style={{ 
                fontSize: '0.95rem', 
                lineHeight: '1.6',
                color: '#ddd',
                whiteSpace: 'pre-wrap'
              }}>
                {analysis.technical_analysis}
              </div>
            </div>
          )}

          {/* Recommendation */}
          {analysis.recommendation && (
            <div style={{
              padding: '1.5rem',
              borderTop: '1px solid #1e2329',
              background: '#1a1f25'
            }}>
              <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '0.75rem' }}>
                💡 Recommendation
              </div>
              <div style={{ 
                fontSize: '1rem', 
                lineHeight: '1.6',
                color: '#00ff88'
              }}>
                {analysis.recommendation}
              </div>
            </div>
          )}
        </>
      )}

      {/* Footer */}
      <div style={{
        padding: '1rem',
        borderTop: '1px solid #1e2329',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#666'
      }}>
        ⚠️ AI analysis for informational purposes only. Not financial advice.
      </div>
    </div>
  );
}
