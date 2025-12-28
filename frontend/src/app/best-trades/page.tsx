'use client';

import BestTradesDashboard from '@/components/BestTradesDashboard';

export default function BestTradesPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  return <BestTradesDashboard apiUrl={apiUrl} />;
}
