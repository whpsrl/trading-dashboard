// lib/api.ts o utils/api.ts nel tuo frontend Next.js

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-dashboard-production-79d9.up.railway.app';

// ✅ CORRETTI - Aggiungi /api/v1/market-data prefix
export const API_ENDPOINTS = {
  // Market Data
  marketData: `${API_BASE_URL}/api/v1/market-data`,
  crypto: (symbol: string) => `${API_BASE_URL}/api/v1/market-data/crypto/${symbol}`,
  forex: (symbol: string) => `${API_BASE_URL}/api/v1/market-data/forex/${symbol}`,
  stock: (symbol: string) => `${API_BASE_URL}/api/v1/market-data/stock/${symbol}`,
  
  // AI Analysis
  aiAnalyze: `${API_BASE_URL}/api/v1/ai/analyze`,
  
  // Health
  health: `${API_BASE_URL}/api/v1/health`,
};

// Helper function per fetch crypto data
export async function fetchCryptoData(
  symbol: string,
  timeframe: string = '1h',
  limit: number = 1000
) {
  const url = `${API_ENDPOINTS.crypto(symbol)}?timeframe=${timeframe}&limit=${limit}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status} - ${response.statusText}`);
  }
  
  return response.json();
}

// Helper per market data aggregato
export async function fetchMarketData() {
  const response = await fetch(API_ENDPOINTS.marketData);
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}
