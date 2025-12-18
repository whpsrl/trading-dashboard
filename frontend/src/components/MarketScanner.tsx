'use client';

export default function marketscanner() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to right, #f97316, #ef4444)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      padding: '20px'
    }}>
      <h1 style={{
        fontSize: '120px',
        color: 'white',
        fontWeight: 'bold',
        textShadow: '4px 4px 8px rgba(0,0,0,0.3)',
        margin: '0'
      }}>
        🍝 TRIPPA 🍝
      </h1>
      <p style={{
        fontSize: '32px',
        color: 'white',
        marginTop: '20px',
        textAlign: 'center'
      }}>
        Se vedi questa pagina, la cache è stata bypassata! ✅
      </p>
      <p style={{
        fontSize: '20px',
        color: 'rgba(255,255,255,0.8)',
        marginTop: '10px'
      }}>
        Timestamp: {new Date().toISOString()}
      </p>
    </div>
  );
}
