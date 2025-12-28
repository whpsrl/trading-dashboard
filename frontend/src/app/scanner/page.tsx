'use client';

import MarketScanner from '@/components/MarketScanner';
import Navbar from '@/components/Navbar';

export default function ScannerPage() {
  return (
    <>
      <Navbar />
      <main style={{ minHeight: 'calc(100vh - 80px)', background: '#0a0e13' }}>
        <MarketScanner />
      </main>
    </>
  );
}
