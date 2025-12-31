'use client'

import { useState, useEffect } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function TradesPage() {
  const [setups, setSetups] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState({
    status: 'all',
    timeframe: 'all',
    limit: 100
  })

  useEffect(() => {
    fetchSetups()
  }, [filter])

  const fetchSetups = async () => {
    try {
      setLoading(true)
      setError(null)

      let url = `${BACKEND_URL}/api/setups/all?limit=${filter.limit}`
      if (filter.status !== 'all') url += `&status=${filter.status}`
      if (filter.timeframe !== 'all') url += `&timeframe=${filter.timeframe}`

      const response = await fetch(url)
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      const data = await response.json()
      
      setSetups(data.setups || [])
    } catch (e) {
      console.error("Failed to fetch setups:", e)
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return '#3b82f6'
      case 'hit_tp': return '#10b981'
      case 'hit_sl': return '#ef4444'
      case 'expired': return '#9ca3af'
      default: return '#6b7280'
    }
  }

  const getDirectionColor = (direction: string) => {
    switch (direction) {
      case 'LONG': return '#10b981'
      case 'SHORT': return '#ef4444'
      default: return '#9ca3af'
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem' }}>
      <div style={{ fontSize: '2rem' }}>Loading trades...</div>
    </div>
  )

  if (error) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'red' }}>
      Error: {error}
    </div>
  )

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 1.5rem' }}>
      <h1 style={{
        fontSize: '2.5rem',
        fontWeight: 'bold',
        marginBottom: '1rem',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        📋 All Trades & Setups
      </h1>

      <p style={{
        fontSize: '1.1rem',
        color: '#666',
        marginBottom: '2rem'
      }}>
        Complete list of all trading setups from manual and auto scans (Crypto, Commodities, Indices)
      </p>

      {/* Filters */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1.5rem',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        marginBottom: '2rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '600', color: '#555', marginBottom: '0.5rem' }}>
            Status
          </label>
          <select 
            value={filter.status}
            onChange={(e) => setFilter({...filter, status: e.target.value})}
            style={{
              width: '100%',
              padding: '0.5rem',
              borderRadius: '6px',
              border: '1px solid #e5e7eb'
            }}
          >
            <option value="all">All</option>
            <option value="open">Open</option>
            <option value="hit_tp">Hit TP (Win)</option>
            <option value="hit_sl">Hit SL (Loss)</option>
            <option value="expired">Expired</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '600', color: '#555', marginBottom: '0.5rem' }}>
            Timeframe
          </label>
          <select 
            value={filter.timeframe}
            onChange={(e) => setFilter({...filter, timeframe: e.target.value})}
            style={{
              width: '100%',
              padding: '0.5rem',
              borderRadius: '6px',
              border: '1px solid #e5e7eb'
            }}
          >
            <option value="all">All</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
            <option value="4h">4h</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '600', color: '#555', marginBottom: '0.5rem' }}>
            Limit
          </label>
          <select 
            value={filter.limit}
            onChange={(e) => setFilter({...filter, limit: Number(e.target.value)})}
            style={{
              width: '100%',
              padding: '0.5rem',
              borderRadius: '6px',
              border: '1px solid #e5e7eb'
            }}
          >
            <option value="50">Last 50</option>
            <option value="100">Last 100</option>
            <option value="200">Last 200</option>
            <option value="500">Last 500</option>
          </select>
        </div>
      </div>

      {/* Stats Summary */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1.5rem',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        marginBottom: '2rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '1rem'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
            {setups?.length || 0}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#666' }}>Total Setups</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#3b82f6' }}>
            {setups?.filter(s => s.status === 'open').length || 0}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#666' }}>Open</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
            {setups?.filter(s => s.status === 'hit_tp').length || 0}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#666' }}>Wins</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>
            {setups?.filter(s => s.status === 'hit_sl').length || 0}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#666' }}>Losses</div>
        </div>
      </div>

      {/* Trades Table */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        overflow: 'hidden'
      }}>
        {!setups || setups.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#999' }}>
            No setups found with current filters
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ background: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                <tr>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>Date</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>Symbol</th>
                  <th style={{ padding: '1rem', textAlign: 'center', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>TF</th>
                  <th style={{ padding: '1rem', textAlign: 'center', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>Direction</th>
                  <th style={{ padding: '1rem', textAlign: 'center', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>Conf%</th>
                  <th style={{ padding: '1rem', textAlign: 'right', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>Entry</th>
                  <th style={{ padding: '1rem', textAlign: 'right', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>TP</th>
                  <th style={{ padding: '1rem', textAlign: 'right', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>SL</th>
                  <th style={{ padding: '1rem', textAlign: 'center', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>Status</th>
                  <th style={{ padding: '1rem', textAlign: 'right', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>P/L%</th>
                </tr>
              </thead>
              <tbody>
                {setups.map((setup, index) => (
                  <tr key={setup.id || index} style={{
                    borderBottom: '1px solid #f3f4f6',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f9fafb'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                  >
                    <td style={{ padding: '1rem', fontSize: '0.85rem', color: '#6b7280' }}>
                      {formatDate(setup.created_at)}
                    </td>
                    <td style={{ padding: '1rem', fontSize: '0.9rem', fontWeight: '600', color: '#111827' }}>
                      {setup.symbol}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        fontWeight: '600',
                        background: '#eff6ff',
                        color: '#1e40af'
                      }}>
                        {setup.timeframe}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        fontWeight: '700',
                        background: setup.direction === 'LONG' ? '#d1fae5' : setup.direction === 'SHORT' ? '#fee2e2' : '#f3f4f6',
                        color: getDirectionColor(setup.direction)
                      }}>
                        {setup.direction}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center', fontSize: '0.9rem', fontWeight: '600', color: '#374151' }}>
                      {setup.confidence}%
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', fontSize: '0.9rem', color: '#374151' }}>
                      ${setup.entry?.toFixed(2)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', fontSize: '0.9rem', color: '#10b981' }}>
                      ${setup.take_profit?.toFixed(2)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', fontSize: '0.9rem', color: '#ef4444' }}>
                      ${setup.stop_loss?.toFixed(2)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        background: setup.status === 'open' ? '#dbeafe' : setup.status === 'hit_tp' ? '#d1fae5' : setup.status === 'hit_sl' ? '#fee2e2' : '#f3f4f6',
                        color: getStatusColor(setup.status)
                      }}>
                        {setup.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{
                      padding: '1rem',
                      textAlign: 'right',
                      fontSize: '0.9rem',
                      fontWeight: '700',
                      color: setup.profit_loss_pct > 0 ? '#10b981' : setup.profit_loss_pct < 0 ? '#ef4444' : '#6b7280'
                    }}>
                      {setup.profit_loss_pct !== null && setup.profit_loss_pct !== undefined
                        ? `${setup.profit_loss_pct > 0 ? '+' : ''}${setup.profit_loss_pct.toFixed(2)}%`
                        : '-'
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info */}
      <div style={{
        marginTop: '2rem',
        padding: '1rem',
        background: '#f9fafb',
        borderRadius: '8px',
        fontSize: '0.9rem',
        color: '#6b7280'
      }}>
        💡 <strong>Tip:</strong> This page shows all trading setups from the database (manual + auto scans). Data persists across page changes. Use filters to find specific setups.
      </div>
    </div>
  )
}

