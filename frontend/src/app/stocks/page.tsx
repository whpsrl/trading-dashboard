export default function StocksPage() {
  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '0 1.5rem'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '4rem 2.5rem',
        boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}>
          📈
        </div>
        
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          marginBottom: '1rem',
          color: '#1f2937'
        }}>
          Stocks Scanner
        </h1>
        
        <p style={{
          fontSize: '1.25rem',
          color: '#6b7280',
          marginBottom: '2rem'
        }}>
          Coming Soon
        </p>
        
        <div style={{
          padding: '1.5rem',
          background: '#fef3c7',
          borderRadius: '12px',
          border: '2px dashed #f59e0b'
        }}>
          <p style={{
            fontSize: '1rem',
            color: '#92400e',
            margin: 0
          }}>
            🚧 <strong>In Costruzione</strong> - NYSE, NASDAQ, TSX, LSE
          </p>
        </div>
      </div>
    </div>
  )
}

