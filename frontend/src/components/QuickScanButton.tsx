// QuickScanButton.tsx - Aggiungi questo nel ChartAnalyzer

import { useState } from 'react';
import Link from 'next/link';

export function QuickScanButton() {
  const [scanning, setScanning] = useState(false);
  const [quickResults, setQuickResults] = useState<any>(null);

  const runQuickScan = async () => {
    setScanning(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://trading-dashboard-production-79d9.up.railway.app';
      const response = await fetch(`${apiUrl}/api/scanner/scan?timeframe=1h&min_score=7.5&top_n=3`, {
        method: 'POST'
      });
      
      const data = await response.json();
      setQuickResults(data);
    } catch (error) {
      console.error('Quick scan failed:', error);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Quick Scan Button */}
      <div className="flex gap-2">
        <button
          onClick={runQuickScan}
          disabled={scanning}
          className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-4 py-2 rounded-lg font-semibold disabled:opacity-50 transition-all"
        >
          {scanning ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Scanning...
            </span>
          ) : (
            '🔍 Quick Scan (Top 3)'
          )}
        </button>
        
        <Link 
          href="/scanner"
          className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-semibold transition-all"
        >
          Full Scan →
        </Link>
      </div>

      {/* Quick Results */}
      {quickResults && quickResults.results && quickResults.results.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 space-y-3">
          <h4 className="font-semibold text-white">🏆 Top 3 Setups Right Now:</h4>
          {quickResults.results.map((result: any, i: number) => (
            <div key={i} className="bg-gray-700 rounded p-3 text-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-white">{result.symbol}</span>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  result.direction === 'LONG' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {result.direction}
                </span>
              </div>
              <div className="text-gray-300 text-xs space-y-1">
                <p>⭐ Score: {result.score}/10</p>
                <p>💰 Entry: ${result.entry?.toFixed(2)}</p>
                <p>🎯 Target: ${result.target_1?.toFixed(2)}</p>
                <p>📊 R:R: 1:{result.risk_reward?.toFixed(1)}</p>
              </div>
            </div>
          ))}
          <div className="text-center">
            <Link 
              href="/scanner"
              className="text-blue-400 hover:text-blue-300 text-sm font-semibold"
            >
              View Full Scan →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
