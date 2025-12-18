import MarketScannerV2 from '@/components/MarketScanner';

// Forza rendering dinamico - NO cache!
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default function ScanPage() {
  return (
    <main className="min-h-screen bg-gray-900">
      <MarketScannerV2 />
    </main>
  );
}
