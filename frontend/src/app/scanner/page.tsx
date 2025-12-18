import MarketScanner from '@/components/MarketScanner';

// Force dynamic rendering - no cache
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default function ScannerPage() {
  return <MarketScanner />;
}
