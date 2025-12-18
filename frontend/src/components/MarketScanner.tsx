'use client';

import { useState } from 'react';

interface ScanResult {
  symbol: string;
  score: number;
  direction: 'LONG' | 'SHORT';
  entry: number;
  stop_loss: number;
  target_1: number;
  target_2: number;
  risk_reward: number;
  confluences: string[];
  reasoning: string;
}

interface ScanResponse {
  success: boolean;
  timestamp: string;
  duration_seconds: number;
  total_analyzed: number;
  valid_setups: number;
  results: ScanResult[];
}

export default function MarketScanner() {
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<ScanResult[]>([]);
  const [scanInfo, setScanInfo] = useState<any>(null);
  const [error, setError] = useState('');
  
  const [timeframe, setTimeframe] = useState('1h');
  const [minScore, setMinScore] = useState(7.0);
  const [topN, setTopN] = useState(10);
  const [scanMode, setScanMode] = useState('top30'); // NEW

  const startScan = async () => {
    setScanning(true);
    setError('');
    setResults([]);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://trading-dashboard-production-79d9.up.railway.app';
      const url = `${apiUrl}/api/scanner/scan?timeframe=${timeframe}&min_score=${minScore}&top_n=${topN}&mode=${scanMode}`;
      
      const response = await fetch(url, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: ScanResponse = await response.json();
      
      if (data.success) {
        setResults(data.results);
        setScanInfo({
          timestamp: data.timestamp,
          duration: data.duration_seconds,
          total: data.total_analyzed,
          valid: data.valid_setups
        });
      } else {
        throw new Error('Scan failed');
      }
      
    } catch (err: any) {
      setError(err.message || 'Scan failed');
      console.error('Scanner error:', err);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">🔍 AI Market Scanner</h1>
        <p className="text-blue-100">
          Scansiona tutte le crypto e trova automaticamente i migliori setup trading con AI
        </p>
      </div>

      {/* Settings */}
      <div className="bg-gray-800 rounded-lg p-6 space-y-4">
        <h2 className="text-xl font-semibold text-white mb-4">⚙️ Impostazioni Scan</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Scan Mode */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Modalità Scan
            </label>
            <select
              value={scanMode}
              onChange={(e) => setScanMode(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600"
              disabled={scanning}
            >
              <option value="top30">Top 30 (veloce)</option>
              <option value="all">TUTTE (~400+ pairs)</option>
            </select>
          </div>

          {/* Timeframe */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Timeframe
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600"
              disabled={scanning}
            >
              <option value="1h">1 Hour</option>
              <option value="4h">4 Hours</option>
              <option value="1d">1 Day</option>
            </select>
          </div>

          {/* Min Score */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Score Minimo (1-10)
            </label>
            <input
              type="number"
              min="1"
              max="10"
              step="0.5"
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600"
              disabled={scanning}
            />
          </div>

          {/* Top N */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Top Risultati
            </label>
            <input
              type="number"
              min="1"
              max="30"
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value))}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600"
              disabled={scanning}
            />
          </div>
        </div>

        {/* Start Button */}
        <button
          onClick={startScan}
          disabled={scanning}
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all ${
            scanning
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600'
          }`}
        >
          {scanning ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Scansione in corso... (2-5 minuti)
            </span>
          ) : (
            '🚀 Avvia Scan Completo'
          )}
        </button>

        {scanning && (
          <div className="text-center text-gray-400 text-sm">
            <p>Analizzando 30 crypto con Claude AI...</p>
            <p className="mt-1">Questo può richiedere qualche minuto ☕</p>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">❌ {error}</p>
        </div>
      )}

      {/* Scan Info */}
      {scanInfo && (
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-gray-400 text-sm">Analizzate</p>
              <p className="text-2xl font-bold text-white">{scanInfo.total}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Setup Validi</p>
              <p className="text-2xl font-bold text-green-400">{scanInfo.valid}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Durata</p>
              <p className="text-2xl font-bold text-blue-400">{scanInfo.duration}s</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-purple-400">
                {((scanInfo.valid / scanInfo.total) * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white">
            🏆 Top {results.length} Trading Setups
          </h2>
          
          {results.map((result, index) => (
            <div
              key={result.symbol}
              className="bg-gray-800 rounded-lg p-6 border-l-4 hover:bg-gray-750 transition-colors"
              style={{
                borderLeftColor: result.direction === 'LONG' ? '#10b981' : '#ef4444'
              }}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-bold text-gray-400">#{index + 1}</span>
                  <div>
                    <h3 className="text-xl font-bold text-white">{result.symbol}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        result.direction === 'LONG' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {result.direction}
                      </span>
                      <span className="text-yellow-400 font-bold">
                        ⭐ {result.score}/10
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-gray-400 text-sm">Risk/Reward</p>
                  <p className="text-2xl font-bold text-purple-400">
                    1:{result.risk_reward.toFixed(1)}
                  </p>
                </div>
              </div>

              {/* Price Levels */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-700 rounded p-3">
                  <p className="text-gray-400 text-xs mb-1">Entry</p>
                  <p className="text-white font-bold">${result.entry.toFixed(2)}</p>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <p className="text-gray-400 text-xs mb-1">Stop Loss</p>
                  <p className="text-red-400 font-bold">${result.stop_loss.toFixed(2)}</p>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <p className="text-gray-400 text-xs mb-1">Target 1</p>
                  <p className="text-green-400 font-bold">${result.target_1.toFixed(2)}</p>
                </div>
                <div className="bg-gray-700 rounded p-3">
                  <p className="text-gray-400 text-xs mb-1">Target 2</p>
                  <p className="text-green-400 font-bold">${result.target_2.toFixed(2)}</p>
                </div>
              </div>

              {/* Confluences */}
              <div className="mb-3">
                <p className="text-gray-400 text-sm mb-2 font-semibold">Confluenze Tecniche:</p>
                <div className="flex flex-wrap gap-2">
                  {result.confluences.map((conf, i) => (
                    <span
                      key={i}
                      className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm"
                    >
                      ✓ {conf}
                    </span>
                  ))}
                </div>
              </div>

              {/* Reasoning */}
              <div className="bg-gray-900/50 rounded p-3">
                <p className="text-gray-300 text-sm">{result.reasoning}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results */}
      {!scanning && results.length === 0 && scanInfo && (
        <div className="bg-gray-800 rounded-lg p-12 text-center">
          <p className="text-gray-400 text-lg">
            Nessun setup valido trovato con score &gt;= {minScore}
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Prova ad abbassare il min_score o cambiare timeframe
          </p>
        </div>
      )}
    </div>
  );
}
