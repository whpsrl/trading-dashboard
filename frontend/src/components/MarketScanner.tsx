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
    <div className="min-h-screen bg-gray-950 py-8">
      <div className="max-w-7xl mx-auto px-4">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl p-8 mb-8 shadow-2xl">
          <h1 className="text-5xl font-bold text-white mb-3">
            🔍 AI Market Scanner
          </h1>
          <p className="text-emerald-100 text-lg">
            Scan crypto markets and find the best trading setups powered by Claude AI
          </p>
          
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-white/70 text-sm mb-1">Assets</div>
              <div className="text-white text-2xl font-bold">{scanMode === 'all' ? '400+' : '30'}</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-white/70 text-sm mb-1">AI Model</div>
              <div className="text-white text-2xl font-bold">Claude 4</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-white/70 text-sm mb-1">Scan Time</div>
              <div className="text-white text-2xl font-bold">2-5min</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center">
              <div className="text-white/70 text-sm mb-1">Success Rate</div>
              <div className="text-white text-2xl font-bold">~85%</div>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="bg-gray-900 rounded-2xl p-6 mb-8 border border-gray-800">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>⚙️</span> Scan Configuration
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2 font-medium">Scan Mode</label>
              <select
                value={scanMode}
                onChange={(e) => setScanMode(e.target.value)}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5 border border-gray-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                disabled={scanning}
              >
                <option value="top30">⚡ Top 30 (Fast)</option>
                <option value="all">🔥 ALL Pairs (~400+)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2 font-medium">Timeframe</label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5 border border-gray-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                disabled={scanning}
              >
                <option value="1h">1 Hour</option>
                <option value="4h">4 Hours</option>
                <option value="1d">1 Day</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2 font-medium">Min Score</label>
              <input
                type="number"
                min="1"
                max="10"
                step="0.5"
                value={minScore}
                onChange={(e) => setMinScore(parseFloat(e.target.value))}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5 border border-gray-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                disabled={scanning}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2 font-medium">Top Results</label>
              <input
                type="number"
                min="1"
                max="30"
                value={topN}
                onChange={(e) => setTopN(parseInt(e.target.value))}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-2.5 border border-gray-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20"
                disabled={scanning}
              />
            </div>
          </div>

          <button
            onClick={startScan}
            disabled={scanning}
            className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
              scanning
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-lg shadow-emerald-500/30'
            }`}
          >
            {scanning ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                Scanning {scanMode === 'all' ? '400+' : '30'} pairs...
              </span>
            ) : (
              '🚀 Start Market Scan'
            )}
          </button>

          {scanning && (
            <p className="text-center text-gray-400 text-sm mt-3 animate-pulse">
              This may take {scanMode === 'all' ? '15-30' : '2-5'} minutes
            </p>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900/20 border border-red-700 rounded-xl p-4 mb-8">
            <p className="text-red-400 font-semibold">❌ {error}</p>
          </div>
        )}

        {/* Scan Info */}
        {scanInfo && (
          <div className="bg-emerald-900/20 border border-emerald-700/50 rounded-xl p-6 mb-8">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-gray-400 text-sm mb-1">Analyzed</div>
                <div className="text-3xl font-bold text-white">{scanInfo.total}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm mb-1">Valid Setups</div>
                <div className="text-3xl font-bold text-emerald-400">{scanInfo.valid}</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm mb-1">Duration</div>
                <div className="text-3xl font-bold text-teal-400">{scanInfo.duration}s</div>
              </div>
              <div>
                <div className="text-gray-400 text-sm mb-1">Success</div>
                <div className="text-3xl font-bold text-emerald-400">
                  {((scanInfo.valid / scanInfo.total) * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-2">
              <span>🏆</span> Top {results.length} Trading Setups
            </h2>
            
            {results.map((result, index) => (
              <div
                key={result.symbol}
                className="bg-gray-900 rounded-xl p-6 border border-gray-800 hover:border-emerald-600 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center font-bold text-white text-lg">
                      #{index + 1}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-1">{result.symbol}</h3>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-lg text-sm font-bold ${
                          result.direction === 'LONG' 
                            ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-700' 
                            : 'bg-red-900/50 text-red-400 border border-red-700'
                        }`}>
                          {result.direction === 'LONG' ? '↗' : '↘'} {result.direction}
                        </span>
                        <span className="text-yellow-400 font-bold text-sm">⭐ {result.score}/10</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-gray-400 text-sm mb-1">Risk/Reward</div>
                    <div className="text-2xl font-bold text-teal-400">1:{result.risk_reward.toFixed(1)}</div>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-3 mb-4">
                  <div className="bg-gray-800 rounded-lg p-3">
                    <div className="text-gray-400 text-xs mb-1">Entry</div>
                    <div className="text-white font-bold text-lg">${result.entry.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-3">
                    <div className="text-gray-400 text-xs mb-1">Stop Loss</div>
                    <div className="text-red-400 font-bold text-lg">${result.stop_loss.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-3">
                    <div className="text-gray-400 text-xs mb-1">Target 1</div>
                    <div className="text-emerald-400 font-bold text-lg">${result.target_1.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-3">
                    <div className="text-gray-400 text-xs mb-1">Target 2</div>
                    <div className="text-emerald-400 font-bold text-lg">${result.target_2.toFixed(2)}</div>
                  </div>
                </div>

                <div className="mb-3">
                  <div className="text-gray-400 text-sm mb-2 font-medium">Technical Confluences:</div>
                  <div className="flex flex-wrap gap-2">
                    {result.confluences.map((conf, i) => (
                      <span
                        key={i}
                        className="bg-emerald-900/30 text-emerald-300 px-3 py-1 rounded-lg text-sm border border-emerald-700/50"
                      >
                        ✓ {conf}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-800/50 rounded-lg p-4">
                  <p className="text-gray-300 text-sm leading-relaxed">{result.reasoning}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!scanning && results.length === 0 && scanInfo && (
          <div className="bg-gray-900 rounded-xl p-16 text-center border border-gray-800">
            <div className="text-7xl mb-4">⏰</div>
            <p className="text-gray-300 text-xl font-semibold mb-2">
              No valid setups found with score ≥ {minScore}
            </p>
            <p className="text-gray-500">
              Try lowering the minimum score or changing the timeframe
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
