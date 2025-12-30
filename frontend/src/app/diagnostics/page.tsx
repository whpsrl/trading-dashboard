'use client'

import { useState, useEffect } from 'react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-dashboard-production-79d9.up.railway.app'

export default function DiagnosticsPage() {
  const [health, setHealth] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [testClaude, setTestClaude] = useState<any>(null)
  const [testGroq, setTestGroq] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    runAllChecks()
  }, [])

  const runAllChecks = async () => {
    setLoading(true)
    
    // Health check
    try {
      const res = await fetch(`${BACKEND_URL}/api/health`)
      const data = await res.json()
      setHealth(data)
    } catch (error) {
      setHealth({ error: 'Backend offline' })
    }

    // Stats
    try {
      const res = await fetch(`${BACKEND_URL}/api/stats`)
      const data = await res.json()
      setStats(data)
    } catch (error) {
      setStats({ error: 'Failed to load stats' })
    }

    // Claude test
    try {
      const res = await fetch(`${BACKEND_URL}/api/scan/test?ai_provider=claude`)
      const data = await res.json()
      setTestClaude(data)
    } catch (error) {
      setTestClaude({ error: 'Failed to test Claude' })
    }

    // Groq test
    try {
      const res = await fetch(`${BACKEND_URL}/api/scan/test?ai_provider=groq`)
      const data = await res.json()
      setTestGroq(data)
    } catch (error) {
      setTestGroq({ error: 'Failed to test Groq' })
    }

    setLoading(false)
  }

  const testTelegram = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/test/telegram`)
      const data = await res.json()
      alert(data.success ? '✅ Telegram test sent!' : '❌ Telegram test failed')
    } catch (error) {
      alert('❌ Error testing Telegram')
    }
  }

  return (
    <div style={{
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '0 1.5rem'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <h1 style={{
          fontSize: '2.25rem',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🔧 System Diagnostics
        </h1>

        <button
          onClick={runAllChecks}
          disabled={loading}
          style={{
            background: loading ? '#ccc' : '#667eea',
            color: 'white',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '⏳ Checking...' : '🔄 Refresh All'}
        </button>
      </div>

      {/* Health Status */}
      <CheckSection
        title="🏥 Health Status"
        status={health?.status === 'online' ? 'success' : 'error'}
        data={health}
      />

      {/* Service Availability */}
      {health && (
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '1.5rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
            📡 Services
          </h2>
          
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            <ServiceStatus label="Scanner" available={health.scanner_available} />
            <ServiceStatus label="AI (Claude)" available={health.ai_available} />
            <ServiceStatus label="Telegram" available={health.telegram_available} />
          </div>

          <button
            onClick={testTelegram}
            style={{
              marginTop: '1rem',
              background: '#10b981',
              color: 'white',
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
              width: '100%'
            }}
          >
            📱 Send Test Alert to Telegram
          </button>
        </div>
      )}

      {/* Stats */}
      <CheckSection
        title="📊 Database & Learning"
        status={stats?.success ? 'success' : 'error'}
        data={stats?.stats || stats}
      />

      {/* AI Tests */}
      <CheckSection
        title="🧪 Claude AI Test (BTC/USDT 1h)"
        status={testClaude?.success ? 'success' : 'error'}
        data={testClaude?.analysis || testClaude}
      />

      <CheckSection
        title="⚡ Groq AI Test (BTC/USDT 1h)"
        status={testGroq?.success ? 'success' : 'error'}
        data={testGroq?.analysis || testGroq}
      />

      {/* Backend URL */}
      <div style={{
        background: '#f9fafb',
        borderRadius: '12px',
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          🌐 Backend URL
        </h2>
        <code style={{
          display: 'block',
          background: '#1f2937',
          color: '#10b981',
          padding: '1rem',
          borderRadius: '6px',
          fontSize: '0.875rem',
          overflowX: 'auto'
        }}>
          {BACKEND_URL}
        </code>
      </div>

      {/* Quick Links */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '1.5rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          🔗 Quick API Links
        </h2>
        
        <div style={{ display: 'grid', gap: '0.5rem', fontSize: '0.875rem' }}>
          <ApiLink href={`${BACKEND_URL}`} label="Root" />
          <ApiLink href={`${BACKEND_URL}/api/health`} label="Health Check" />
          <ApiLink href={`${BACKEND_URL}/api/stats`} label="Statistics" />
          <ApiLink href={`${BACKEND_URL}/api/results`} label="Recent Results" />
          <ApiLink href={`${BACKEND_URL}/api/scan/test`} label="BTC Test" />
        </div>
      </div>
    </div>
  )
}

function CheckSection({ title, status, data }: any) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      border: `2px solid ${status === 'success' ? '#10b981' : status === 'error' ? '#ef4444' : '#e5e7eb'}`
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>
          {title}
        </h2>
        <span style={{
          background: status === 'success' ? '#d1fae5' : '#fee2e2',
          color: status === 'success' ? '#065f46' : '#991b1b',
          padding: '0.375rem 0.875rem',
          borderRadius: '9999px',
          fontSize: '0.875rem',
          fontWeight: '600'
        }}>
          {status === 'success' ? '✅ OK' : '❌ ERROR'}
        </span>
      </div>

      <pre style={{
        background: '#f9fafb',
        padding: '1rem',
        borderRadius: '6px',
        fontSize: '0.75rem',
        overflow: 'auto',
        maxHeight: '300px'
      }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}

function ServiceStatus({ label, available }: any) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.75rem',
      background: '#f9fafb',
      borderRadius: '6px'
    }}>
      <span style={{ fontWeight: '600' }}>{label}</span>
      <span style={{
        color: available ? '#10b981' : '#ef4444',
        fontWeight: 'bold'
      }}>
        {available ? '✅ Available' : '❌ Unavailable'}
      </span>
    </div>
  )
}

function ApiLink({ href, label }: any) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: 'block',
        padding: '0.75rem',
        background: '#f9fafb',
        borderRadius: '6px',
        textDecoration: 'none',
        color: '#667eea',
        fontWeight: '600',
        transition: 'background 0.2s'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = '#eff6ff'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = '#f9fafb'
      }}
    >
      {label} →
    </a>
  )
}

