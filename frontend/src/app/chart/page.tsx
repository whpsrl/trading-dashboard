'use client';

import ChartAnalyzer from '@/components/ChartAnalyzer';
import Navbar from '@/components/Navbar';

export default function ChartPage() {
  return (
    <>
      <Navbar />
      <main className="w-full" style={{ height: 'calc(100vh - 80px)' }}>
        <ChartAnalyzer />
      </main>
    </>
  );
}

