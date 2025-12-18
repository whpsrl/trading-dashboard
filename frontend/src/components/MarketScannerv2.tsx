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

export default function marketscannerv2() {
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<ScanResult[]>([]);
  const [scanInfo, setScanInfo] = useState<any>(null);
  const [error, setError] = useState('');
  
  const [timeframe, setTimeframe] = useState('1h');
  const [minScore, setMinScore] = useState(7.0);
  const [topN, setTopN] = useState(10);
  const [scanMode, setScanMode] = useState('top30');

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
    <div className="min-h-screen bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Header Semplice */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl p-8 mb-8 shadow-2xl">
          <h1 className="text-4xl font-bold text-white mb-2">
            🔍 AI Market Scanner
          </h1>
          <p className="text-emerald-100">
            Scan the market and find the best trading opportunities with AI
          </p>
          
          {/* Stats semplici */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <div className="text-white/60 text-xs">Assets</div>
              <div className="text-white text-xl font-bold">{scanMode === 'all' ? '400+' : '30'}</div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <div className="text-white/60 text-xs">AI Model</div>
              <div className="text-white text-xl font-bold">Claude</div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <div className="text-white/60 text-xs">Time</div>
              <div className="text-white text-xl font-bold">2-5min</div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <div className="text-white/60 text-xs">Accuracy</div>
              <div className="text-white text-xl font-bold">85%</div>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="bg-gray-900 rounded-xl p-6 mb-8 border border-gray-800">
          <h2 className="text-xl font-bold text-white mb-4">⚙️ Configuration</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Scan Mode</label>
              <select
                value={scanMode}
                onChange={(e) => setScanMode(e.target.value)}
                className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700"
                disabled={scanning}
              >
                <option value="top30">Top 30</option>
                <option value="all">ALL (~400+)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Timeframe</label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700"
                disabled={scanning}
              >
                <option value="1h">1 Hour</option>
                <option value="4h">4 Hours</option>
                <option value="1d">1 Day</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Min Score</label>
              <input
                type="number"
                min="1"
                max="10"
                step="0.5"
                value={minScore}
                onChange={(e) => setMinScore(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700"
                disabled={scanning}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Top Results</label>
              <input
                type="number"
                min="1"
                max="30"
                value={topN}
                onChange={(e) => setTopN(parseInt(e.target.value))}
                className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700"
                disabled={scanning}
              />
            </div>
          </div>

          <button
            onClick={startScan}
            disabled={scanning}
            className={`w-full py-3 rounded-lg font-bold transition-all ${
              scanning
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white'
            }`}
          >
            {scanning ? '⏳ Scanning...' : '🚀 Start Market Scan'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 mb-8">
            <p className="text-red-400">❌ {error}</p>
          </div>
        )}

        {/* Scan Info */}
        {scanInfo && (
          <div className="bg-emerald-900/20 border border-emerald-700/50 rounded-lg p-6 mb-8">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-gray-400 text-sm">Analyzed</div>
                <div className="text-2xl font-bold text-white">{scanInfo.total}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Valid Setups</div>
                <div className="text-2xl font-bold text-emerald-400">{scanInfo.valid}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Duration</div>
                <div className="text-2xl font-bold text-teal-400">{scanInfo.duration}s</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm">Success</div>
                <div className="text-2xl font-bold text-emerald-400">
                  {((scanInfo.valid / scanInfo.total) * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-white mb-4">
              🏆 Top {results.length} Trading Setups
            </h2>
            
            {results.map((result, index) => (
              <div
                key={result.symbol}
                className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-emerald-700 transition-all"
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-emerald-700 rounded-lg flex items-center justify-center font-bold text-white">
                      #{index + 1}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{result.symbol}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          result.direction === 'LONG' 
                            ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-700' 
                            : 'bg-red-900/50 text-red-400 border border-red-700'
                        }`}>
                          {result.direction === 'LONG' ? '↗' : '↘'} {result.direction}
                        </span>
                        <span className="text-yellow-400 font-bold">⭐ {result.score}/10</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-gray-400 text-sm">R:R</div>
                    <div className="text-2xl font-bold text-teal-400">1:{result.risk_reward.toFixed(1)}</div>
                  </div>
                </div>

                {/* Price Levels */}
                <div className="grid grid-cols-4 gap-3 mb-4">
                  <div className="bg-gray-800 rounded p-3">
                    <div className="text-gray-400 text-xs mb-1">Entry</div>
                    <div className="text-white font-bold">${result.entry.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-800 rounded p-3">
                    <div className="text-gray-400 text-xs mb-1">Stop Loss</div>
                    <div className="text-red-400 font-bold">${result.stop_loss.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-800 rounded p-3">
                    <div className="text-gray-400 text-xs mb-1">Target 1</div>
                    <div className="text-emerald-400 font-bold">${result.target_1.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-800 rounded p-3">
                    <div className="text-gray-400 text-xs mb-1">Target 2</div>
                    <div className="text-emerald-400 font-bold">${result.target_2.toFixed(2)}</div>
                  </div>
                </div>

                {/* Confluences */}
                <div className="mb-3">
                  <div className="text-gray-400 text-sm mb-2">Confluences:</div>
                  <div className="flex flex-wrap gap-2">
                    {result.confluences.map((conf, i) => (
                      <span
                        key={i}
                        className="bg-emerald-900/30 text-emerald-300 px-2 py-1 rounded text-sm border border-emerald-700/50"
                      >
                        ✓ {conf}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Reasoning */}
                <div className="bg-gray-800/50 rounded p-3">
                  <p className="text-gray-300 text-sm">{result.reasoning}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!scanning && results.length === 0 && scanInfo && (
          <div className="bg-gray-900 rounded-lg p-12 text-center border border-gray-800">
            <div className="text-6xl mb-4">⏰</div>
            <p className="text-gray-400 text-lg">
              No valid setups found with score ≥ {minScore}
            </p>
            <p className="text-gray-600 text-sm mt-2">
              Try lowering the minimum score
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
