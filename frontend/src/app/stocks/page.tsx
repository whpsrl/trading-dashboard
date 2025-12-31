'use client'

import { useState, useEffect } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function StocksPage() {
  const [categories, setCategories] = useState<any>({})
  const [selectedStocks, setSelectedStocks] = useState<string[]>([])
  const [aiProvider, setAiProvider] = useState('claude')
  const [timeframes, setTimeframes] = useState<string[]>(['4h'])
  const [scanning, setScanning] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStocksList()
  }, [])

  const fetchStocksList = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stocks/list`)
      const data = await response.json()
      if (data.success) {
        setCategories(data.categories)
      }
    } catch (error) {
      console.error('Error fetching stocks list:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleStock = (symbol: string) => {
    setSelectedStocks(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    )
  }

  const selectAll = (categoryStocks: any[]) => {
    const symbols = categoryStocks.map(s => s.symbol)
    const allSelected = symbols.every(s => selectedStocks.includes(s))
    
    if (allSelected) {
      setSelectedStocks(prev => prev.filter(s => !symbols.includes(s)))
    } else {
      setSelectedStocks(prev => {
        const combined = [...prev, ...symbols]
        return Array.from(new Set(combined))
      })
    }
  }

  const toggleTimeframe = (tf: string) => {
    setTimeframes(prev =>
      prev.includes(tf)
        ? prev.filter(t => t !== tf)
        : [...prev, tf]
    )
  }

  const runScan = async () => {
    if (selectedStocks.length === 0) {
      alert('❌ Select at least one stock!')
      return
    }

    if (timeframes.length === 0) {
      alert('❌ Select at least one timeframe!')
      return
    }

    setScanning(true)
    setResults(null)

    try {
      const response = await fetch(`${BACKEND_URL}/api/stocks/scan?ai_provider=${aiProvider}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selected_symbols: selectedStocks,
          timeframes: timeframes
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setResults(data)
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error scanning stocks:', error)
      alert('Failed to scan stocks')
    } finally {
      setScanning(false)
    }
  }

  if (loading) {
    return (
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem 1.5rem', textAlign: 'center' }}>
        <p>Loading stocks...</p>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem', background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        📈 Stocks Scanner
      </h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Select stocks to analyze with AI • {selectedStocks.length} selected
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Left: Stock Selection */}
        <div>
          <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>📊 Select Stocks</h2>
            
            {Object.entries(categories).map(([categoryKey, categoryData]: [string, any]) => {
              const categoryStocks = categoryData.stocks
              const allSelected = categoryStocks.every((s: any) => selectedStocks.includes(s.symbol))
              const someSelected = categoryStocks.some((s: any) => selectedStocks.includes(s.symbol))
              
              return (
                <div key={categoryKey} style={{ marginBottom: '2rem', borderBottom: '1px solid #e5e7eb', paddingBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#374151', margin: 0 }}>
                      {categoryData.name}
                    </h3>
                    <button
                      onClick={() => selectAll(categoryStocks)}
                      style={{
                        padding: '0.5rem 1rem',
                        background: allSelected ? '#ef4444' : someSelected ? '#f59e0b' : '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: 'bold'
                      }}
                    >
                      {allSelected ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.75rem' }}>
                    {categoryStocks.map((stock: any) => {
                      const isSelected = selectedStocks.includes(stock.symbol)
                      return (
                        <button
                          key={stock.symbol}
                          onClick={() => toggleStock(stock.symbol)}
                          style={{
                            padding: '0.75rem 1rem',
                            background: isSelected ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' : '#f3f4f6',
                            color: isSelected ? 'white' : '#374151',
                            border: isSelected ? '2px solid #d97706' : '1px solid #e5e7eb',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            textAlign: 'left',
                            transition: 'all 0.2s',
                            fontWeight: isSelected ? 'bold' : 'normal'
                          }}
                        >
                          <div style={{ fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                            {stock.symbol}
                          </div>
                          <div style={{ fontSize: '0.75rem', opacity: 0.8 }}>
                            {stock.name}
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Results */}
          {results && (
            <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>📊 Results</h2>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <span style={{ padding: '0.5rem 1rem', background: '#f3f4f6', borderRadius: '8px', fontSize: '0.9rem' }}>
                    {results.count} setups
                  </span>
                  <span style={{ padding: '0.5rem 1rem', background: results.high_confidence_count > 0 ? '#10b981' : '#f3f4f6', color: results.high_confidence_count > 0 ? 'white' : '#374151', borderRadius: '8px', fontSize: '0.9rem', fontWeight: 'bold' }}>
                    {results.high_confidence_count} high conf
                  </span>
                </div>
              </div>

              {results.setups.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#9ca3af', padding: '2rem' }}>
                  No high-confidence setups found
                </p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {results.setups.map((setup: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        padding: '1.5rem',
                        background: setup.direction === 'LONG' ? '#f0fdf4' : setup.direction === 'SHORT' ? '#fef2f2' : '#f9fafb',
                        border: `2px solid ${setup.direction === 'LONG' ? '#10b981' : setup.direction === 'SHORT' ? '#ef4444' : '#e5e7eb'}`,
                        borderRadius: '12px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                        <div>
                          <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827', margin: 0, marginBottom: '0.25rem' }}>
                            {setup.symbol}
                          </h3>
                          <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.85rem', color: '#6b7280' }}>
                            <span>{setup.timeframe}</span>
                            <span>•</span>
                            <span>{setup.ai_provider.toUpperCase()}</span>
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                          <span style={{
                            padding: '0.5rem 1rem',
                            background: setup.direction === 'LONG' ? '#10b981' : setup.direction === 'SHORT' ? '#ef4444' : '#6b7280',
                            color: 'white',
                            borderRadius: '8px',
                            fontWeight: 'bold',
                            fontSize: '0.9rem'
                          }}>
                            {setup.direction}
                          </span>
                          <span style={{
                            padding: '0.5rem 1rem',
                            background: setup.confidence >= 80 ? '#10b981' : setup.confidence >= 70 ? '#f59e0b' : '#ef4444',
                            color: 'white',
                            borderRadius: '8px',
                            fontWeight: 'bold',
                            fontSize: '0.9rem'
                          }}>
                            {setup.confidence}%
                          </span>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1rem', padding: '1rem', background: 'white', borderRadius: '8px' }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.25rem' }}>Entry</div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#111827' }}>${setup.entry.toFixed(2)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.25rem' }}>Stop Loss</div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#ef4444' }}>${setup.stop_loss.toFixed(2)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.25rem' }}>Take Profit</div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#10b981' }}>${setup.take_profit.toFixed(2)}</div>
                        </div>
                      </div>

                      <div style={{ padding: '1rem', background: 'white', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '0.5rem', fontWeight: '600' }}>💡 AI Reasoning:</div>
                        <div style={{ fontSize: '0.9rem', color: '#374151', lineHeight: '1.6' }}>
                          {setup.reasoning}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Settings */}
        <div>
          <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 30px rgba(0,0,0,0.08)', position: 'sticky', top: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>⚙️ Settings</h2>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>AI Provider</label>
              <select
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value)}
                style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '1rem' }}
              >
                <option value="claude">🤖 Claude Sonnet 4</option>
                <option value="groq">⚡ Groq (Llama 3.3)</option>
              </select>
            </div>

            <div style={{ marginBottom: '2rem' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Timeframes</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {['15m', '1h', '4h'].map(tf => (
                  <button
                    key={tf}
                    onClick={() => toggleTimeframe(tf)}
                    style={{
                      padding: '0.75rem',
                      background: timeframes.includes(tf) ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' : '#f3f4f6',
                      color: timeframes.includes(tf) ? 'white' : '#374151',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontWeight: timeframes.includes(tf) ? 'bold' : 'normal',
                      transition: 'all 0.2s'
                    }}
                  >
                    {tf.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ padding: '1rem', background: '#fef3c7', borderRadius: '8px', marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '0.85rem', color: '#92400e', marginBottom: '0.5rem' }}>
                <strong>📊 {selectedStocks.length} stocks selected</strong>
              </div>
              <div style={{ fontSize: '0.75rem', color: '#92400e' }}>
                {timeframes.length} timeframe{timeframes.length !== 1 ? 's' : ''} • {aiProvider.toUpperCase()}
              </div>
            </div>

            <button
              onClick={runScan}
              disabled={scanning || selectedStocks.length === 0}
              style={{
                width: '100%',
                padding: '1rem',
                background: scanning || selectedStocks.length === 0 ? '#9ca3af' : 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: scanning || selectedStocks.length === 0 ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '1.1rem',
                transition: 'all 0.2s'
              }}
            >
              {scanning ? '🔄 Scanning...' : '🚀 Scan Selected Stocks'}
            </button>

            {selectedStocks.length === 0 && (
              <p style={{ textAlign: 'center', color: '#ef4444', fontSize: '0.85rem', marginTop: '1rem' }}>
                ⚠️ Select at least one stock
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
