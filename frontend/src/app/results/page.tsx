'use client'

import { useState, useEffect } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function ResultsPage() {
  const [stats, setStats] = useState<any>(null)
  const [scans, setScans] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedScan, setSelectedScan] = useState<any>(null)
  const [scanSetups, setScanSetups] = useState<any[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load stats
      const statsRes = await fetch(`${BACKEND_URL}/api/stats`)
      const statsData = await statsRes.json()
      if (statsData.success) {
        setStats(statsData.stats)
      }

      // Load recent scans
      const scansRes = await fetch(`${BACKEND_URL}/api/results?limit=20`)
      const scansData = await scansRes.json()
      if (scansData.success) {
        setScans(scansData.scans)
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadScanSetups = async (scanId: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/results/${scanId}`)
      const data = await res.json()
      if (data.success) {
        setScanSetups(data.setups)
        setSelectedScan(scans.find(s => s.id === scanId))
      }
    } catch (error) {
      console.error('Error loading scan setups:', error)
    }
  }

  if (loading) {
    return (
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '2rem 1.5rem',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
        <p style={{ fontSize: '1.25rem', color: '#6b7280' }}>Loading results...</p>
      </div>
    )
  }

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '0 1.5rem'
    }}>
      <h1 style={{
        fontSize: '2.25rem',
        fontWeight: 'bold',
        marginBottom: '2rem',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        📊 Results & Auto-Learning
      </h1>

      {/* Stats Cards */}
      {stats && (
        <>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            <StatCard
              title="Total P/L"
              value={`${(stats.total_pl || 0) >= 0 ? '+' : ''}${stats.total_pl || 0}%`}
              icon={(stats.total_pl || 0) >= 0 ? "💰" : "📉"}
              color={(stats.total_pl || 0) >= 0 ? "#10b981" : "#ef4444"}
            />
            <StatCard
              title="Win/Loss"
              value={`${stats.win_count || 0}W / ${stats.loss_count || 0}L`}
              icon="📊"
              color="#667eea"
            />
            <StatCard
              title="Win Rate"
              value={`${stats.win_rate}%`}
              icon="📈"
              color={stats.win_rate >= 60 ? "#10b981" : stats.win_rate >= 50 ? "#f59e0b" : "#ef4444"}
            />
            <StatCard
              title="Avg Profit"
              value={`+${stats.avg_profit}%`}
              icon="💰"
              color="#10b981"
            />
            <StatCard
              title="Avg Loss"
              value={`-${stats.avg_loss}%`}
              icon="🛑"
              color="#ef4444"
            />
            <StatCard
              title="Expected Value"
              value={`${(stats.expected_value || 0) >= 0 ? '+' : ''}${stats.expected_value || 0}%`}
              icon="🎲"
              color={(stats.expected_value || 0) >= 0 ? "#10b981" : "#ef4444"}
            />
            <StatCard
              title="Risk/Reward"
              value={`${(stats.risk_reward || 0).toFixed(2)}:1`}
              icon="⚖️"
              color={(stats.risk_reward || 0) >= 2 ? "#10b981" : (stats.risk_reward || 0) >= 1.5 ? "#f59e0b" : "#ef4444"}
            />
            <StatCard
              title="Learning Score"
              value={stats.learning_score}
              icon="🧠"
              color="#f59e0b"
            />
          </div>

          {/* Detailed Stats */}
          {stats.tracked_trades > 0 && (
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '2rem',
              boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
              marginBottom: '2rem'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                marginBottom: '1.5rem'
              }}>
                📈 Performance Metrics
              </h2>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '1.5rem'
              }}>
                {/* Win/Loss Ratio */}
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: '#6b7280' }}>
                    Win/Loss Distribution
                  </h3>
                  <div style={{
                    background: '#f9fafb',
                    padding: '1rem',
                    borderRadius: '8px'
                  }}>
                    <div style={{ marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                        <span style={{ fontSize: '0.875rem', color: '#10b981', fontWeight: '600' }}>Wins</span>
                        <span style={{ fontSize: '0.875rem', fontWeight: 'bold' }}>{stats.win_rate}%</span>
                      </div>
                      <div style={{
                        height: '8px',
                        background: '#e5e7eb',
                        borderRadius: '4px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${stats.win_rate}%`,
                          background: '#10b981',
                          transition: 'width 0.3s'
                        }} />
                      </div>
                    </div>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                        <span style={{ fontSize: '0.875rem', color: '#ef4444', fontWeight: '600' }}>Losses</span>
                        <span style={{ fontSize: '0.875rem', fontWeight: 'bold' }}>{100 - stats.win_rate}%</span>
                      </div>
                      <div style={{
                        height: '8px',
                        background: '#e5e7eb',
                        borderRadius: '4px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${100 - stats.win_rate}%`,
                          background: '#ef4444',
                          transition: 'width 0.3s'
                        }} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Risk/Reward */}
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: '#6b7280' }}>
                    Risk/Reward Ratio
                  </h3>
                  <div style={{
                    background: '#f9fafb',
                    padding: '1rem',
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{
                      fontSize: '2.5rem',
                      fontWeight: 'bold',
                      color: stats.avg_profit / stats.avg_loss >= 2 ? '#10b981' : '#f59e0b',
                      marginBottom: '0.5rem'
                    }}>
                      {stats.avg_loss > 0 ? (stats.avg_profit / stats.avg_loss).toFixed(2) : 'N/A'}:1
                    </div>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {(stats.risk_reward || 0) >= 2 ? '✅ Excellent' : (stats.risk_reward || 0) >= 1.5 ? '⚠️ Good' : '❌ Needs improvement'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Recent Scans */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: 'bold',
          marginBottom: '1.5rem'
        }}>
          🕐 Recent Scans
        </h2>

        {scans.length === 0 ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
            No scans yet. Run your first scan!
          </p>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {scans.map((scan) => (
              <div
                key={scan.id}
                onClick={() => loadScanSetups(scan.id)}
                style={{
                  padding: '1.25rem',
                  border: '2px solid ' + (selectedScan?.id === scan.id ? '#667eea' : '#e5e7eb'),
                  borderRadius: '12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  background: selectedScan?.id === scan.id ? '#f5f3ff' : 'white'
                }}
                onMouseEnter={(e) => {
                  if (selectedScan?.id !== scan.id) {
                    e.currentTarget.style.borderColor = '#c7d2fe'
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedScan?.id !== scan.id) {
                    e.currentTarget.style.borderColor = '#e5e7eb'
                  }
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                      Scan #{scan.id} - {scan.scan_type}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {new Date(scan.started_at).toLocaleString()} • 
                      {scan.setups_found} setups found • 
                      {scan.duration_seconds?.toFixed(1)}s duration
                    </div>
                  </div>
                  <div style={{
                    background: scan.status === 'completed' ? '#d1fae5' : '#fee2e2',
                    color: scan.status === 'completed' ? '#065f46' : '#991b1b',
                    padding: '0.375rem 0.875rem',
                    borderRadius: '9999px',
                    fontSize: '0.875rem',
                    fontWeight: '600'
                  }}>
                    {scan.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Scan Setups Details */}
      {selectedScan && scanSetups.length > 0 && (
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
          marginTop: '2rem'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            marginBottom: '1.5rem'
          }}>
            🔍 Setups from Scan #{selectedScan.id}
          </h2>

          <div style={{
            display: 'grid',
            gap: '1rem',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))'
          }}>
            {scanSetups.map((setup, idx) => (
              <div key={idx} style={{
                background: 'white',
                border: '2px solid ' + (setup.direction === 'LONG' ? '#10b981' : setup.direction === 'SHORT' ? '#ef4444' : '#6b7280'),
                borderRadius: '12px',
                padding: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>
                    {setup.symbol}
                  </h3>
                  <span style={{
                    background: setup.direction === 'LONG' ? '#d1fae5' : '#fee2e2',
                    color: setup.direction === 'LONG' ? '#065f46' : '#991b1b',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '9999px',
                    fontSize: '0.875rem',
                    fontWeight: 'bold'
                  }}>
                    {setup.direction}
                  </span>
                </div>

                <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.75rem' }}>
                  {setup.timeframe} • {setup.confidence}% confidence
                </div>

                <div style={{
                  background: '#f9fafb',
                  padding: '0.875rem',
                  borderRadius: '8px',
                  fontSize: '0.875rem'
                }}>
                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Entry:</span>
                      <span style={{ fontWeight: 'bold' }}>${setup.entry?.toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>TP:</span>
                      <span style={{ fontWeight: 'bold', color: '#10b981' }}>${setup.take_profit?.toFixed(2)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>SL:</span>
                      <span style={{ fontWeight: 'bold', color: '#ef4444' }}>${setup.stop_loss?.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {setup.status && setup.status !== 'open' && (
                  <div style={{
                    marginTop: '0.75rem',
                    padding: '0.75rem',
                    background: setup.status === 'hit_tp' ? '#d1fae5' : '#fee2e2',
                    borderRadius: '8px',
                    fontSize: '0.875rem',
                    fontWeight: '600'
                  }}>
                    Status: {setup.status} {setup.profit_loss_pct && `(${setup.profit_loss_pct}%)`}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '1.5rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      borderLeft: `4px solid ${color}`
    }}>
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ fontSize: '2rem', fontWeight: 'bold', color, marginBottom: '0.25rem' }}>
        {value}
      </div>
      <div style={{ fontSize: '0.875rem', color: '#6b7280', fontWeight: '600' }}>
        {title}
      </div>
    </div>
  )
}

