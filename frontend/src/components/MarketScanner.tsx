'use client';

import { useState } from 'react';
import { Sparkles, TrendingUp, TrendingDown, Target, Shield, Zap, Clock, Award } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Hero Header */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-1 mb-8">
          <div className="bg-gray-900 rounded-xl p-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white mb-2">
                  AI Market Scanner
                </h1>
                <p className="text-blue-200 text-lg">
                  Powered by Claude Sonnet 4 • Real-time Analysis • Smart Trading Signals
                </p>
              </div>
            </div>
            
            {/* Stats Bar */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <div className="text-gray-400 text-sm mb-1">Assets Tracked</div>
                <div className="text-2xl font-bold text-white">
                  {scanMode === 'all' ? '400+' : '30'}
                </div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <div className="text-gray-400 text-sm mb-1">AI Model</div>
                <div className="text-2xl font-bold text-purple-400">Claude 4</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <div className="text-gray-400 text-sm mb-1">Scan Time</div>
                <div className="text-2xl font-bold text-blue-400">2-5 min</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <div className="text-gray-400 text-sm mb-1">Success Rate</div>
                <div className="text-2xl font-bold text-green-400">~85%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Settings Panel */}
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">Scan Configuration</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            
            {/* Scan Mode */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                📊 Scan Mode
              </label>
              <select
                value={scanMode}
                onChange={(e) => setScanMode(e.target.value)}
                className="w-full bg-gray-900/50 text-white rounded-xl px-4 py-3 border border-gray-600/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                disabled={scanning}
              >
                <option value="top30">⚡ Top 30 (Fast)</option>
                <option value="all">🔥 ALL Pairs (~400+)</option>
              </select>
            </div>

            {/* Timeframe */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                ⏰ Timeframe
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-gray-900/50 text-white rounded-xl px-4 py-3 border border-gray-600/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                disabled={scanning}
              >
                <option value="1h">1 Hour</option>
                <option value="4h">4 Hours</option>
                <option value="1d">1 Day</option>
              </select>
            </div>

            {/* Min Score */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                ⭐ Min Score
              </label>
              <input
                type="number"
                min="1"
                max="10"
                step="0.5"
                value={minScore}
                onChange={(e) => setMinScore(parseFloat(e.target.value))}
                className="w-full bg-gray-900/50 text-white rounded-xl px-4 py-3 border border-gray-600/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                disabled={scanning}
              />
            </div>

            {/* Top N */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                🎯 Top Results
              </label>
              <input
                type="number"
                min="1"
                max="30"
                value={topN}
                onChange={(e) => setTopN(parseInt(e.target.value))}
                className="w-full bg-gray-900/50 text-white rounded-xl px-4 py-3 border border-gray-600/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                disabled={scanning}
              />
            </div>
          </div>

          {/* Start Button */}
          <button
            onClick={startScan}
            disabled={scanning}
            className={`w-full py-4 px-8 rounded-xl font-bold text-lg text-white transition-all transform hover:scale-[1.02] active:scale-[0.98] ${
              scanning
                ? 'bg-gray-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 shadow-lg shadow-purple-500/50'
            }`}
          >
            {scanning ? (
              <span className="flex items-center justify-center gap-3">
                <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <span>Scanning {scanMode === 'all' ? '400+' : '30'} crypto pairs...</span>
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <Sparkles className="w-5 h-5" />
                Launch Full Market Scan
              </span>
            )}
          </button>

          {scanning && (
            <div className="mt-4 text-center">
              <p className="text-gray-400 text-sm animate-pulse">
                ☕ This may take {scanMode === 'all' ? '15-30' : '2-5'} minutes. Analyzing with AI...
              </p>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 mb-8 backdrop-blur-sm">
            <p className="text-red-400 font-semibold">❌ {error}</p>
          </div>
        )}

        {/* Scan Info */}
        {scanInfo && (
          <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/30 rounded-xl p-6 mb-8 backdrop-blur-sm">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-gray-400 text-sm mb-2">Analyzed</div>
                <div className="text-3xl font-bold text-white">{scanInfo.total}</div>
              </div>
              <div className="text-center">
                <div className="text-gray-400 text-sm mb-2">Valid Setups</div>
                <div className="text-3xl font-bold text-green-400">{scanInfo.valid}</div>
              </div>
              <div className="text-center">
                <div className="text-gray-400 text-sm mb-2">Duration</div>
                <div className="text-3xl font-bold text-blue-400">{scanInfo.duration}s</div>
              </div>
              <div className="text-center">
                <div className="text-gray-400 text-sm mb-2">Success Rate</div>
                <div className="text-3xl font-bold text-purple-400">
                  {((scanInfo.valid / scanInfo.total) * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <Award className="w-7 h-7 text-yellow-400" />
              <h2 className="text-3xl font-bold text-white">
                Top {results.length} Trading Opportunities
              </h2>
            </div>
            
            {results.map((result, index) => (
              <div
                key={result.symbol}
                className="group relative bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 overflow-hidden hover:border-gray-600 transition-all duration-300"
              >
                {/* Gradient Border Effect */}
                <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r ${
                  result.direction === 'LONG' 
                    ? 'from-green-500/20 to-transparent' 
                    : 'from-red-500/20 to-transparent'
                }`} />
                
                <div className="relative p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      {/* Rank Badge */}
                      <div className="relative">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center font-bold text-xl ${
                          index === 0 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-gray-900' :
                          index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-gray-900' :
                          index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white' :
                          'bg-gray-700 text-gray-300'
                        }`}>
                          #{index + 1}
                        </div>
                      </div>

                      {/* Symbol & Direction */}
                      <div>
                        <h3 className="text-2xl font-bold text-white mb-2">{result.symbol}</h3>
                        <div className="flex items-center gap-3">
                          <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg text-sm font-bold ${
                            result.direction === 'LONG' 
                              ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                              : 'bg-red-500/20 text-red-400 border border-red-500/50'
                          }`}>
                            {result.direction === 'LONG' ? (
                              <TrendingUp className="w-4 h-4" />
                            ) : (
                              <TrendingDown className="w-4 h-4" />
                            )}
                            {result.direction}
                          </span>
                          <div className="flex items-center gap-1 px-3 py-1 bg-yellow-500/20 rounded-lg border border-yellow-500/50">
                            <span className="text-yellow-400 text-lg">⭐</span>
                            <span className="text-yellow-400 font-bold">{result.score}</span>
                            <span className="text-yellow-400/60 text-sm">/10</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* R:R Badge */}
                    <div className="text-right">
                      <div className="text-gray-400 text-sm mb-1">Risk/Reward</div>
                      <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        1:{result.risk_reward.toFixed(1)}
                      </div>
                    </div>
                  </div>

                  {/* Price Levels */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                    <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-700/50">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="w-4 h-4 text-blue-400" />
                        <span className="text-gray-400 text-xs font-semibold">ENTRY</span>
                      </div>
                      <p className="text-white font-bold text-lg">${result.entry.toFixed(2)}</p>
                    </div>
                    
                    <div className="bg-gray-900/50 rounded-xl p-4 border border-red-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <Shield className="w-4 h-4 text-red-400" />
                        <span className="text-gray-400 text-xs font-semibold">STOP LOSS</span>
                      </div>
                      <p className="text-red-400 font-bold text-lg">${result.stop_loss.toFixed(2)}</p>
                    </div>
                    
                    <div className="bg-gray-900/50 rounded-xl p-4 border border-green-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-green-400 text-xs font-semibold">TARGET 1</span>
                      </div>
                      <p className="text-green-400 font-bold text-lg">${result.target_1.toFixed(2)}</p>
                    </div>
                    
                    <div className="bg-gray-900/50 rounded-xl p-4 border border-green-500/50">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-green-400 text-xs font-semibold">TARGET 2</span>
                      </div>
                      <p className="text-green-400 font-bold text-lg">${result.target_2.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* Confluences */}
                  <div className="mb-4">
                    <p className="text-gray-400 text-sm font-semibold mb-3 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-yellow-400" />
                      Technical Confluences:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {result.confluences.map((conf, i) => (
                        <span
                          key={i}
                          className="inline-flex items-center gap-1 bg-blue-500/10 text-blue-300 px-3 py-1.5 rounded-lg text-sm border border-blue-500/30 font-medium"
                        >
                          <span className="text-blue-400">✓</span>
                          {conf}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Reasoning */}
                  <div className="bg-gray-900/30 rounded-xl p-4 border border-gray-700/30">
                    <p className="text-gray-300 text-sm leading-relaxed">{result.reasoning}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Results */}
        {!scanning && results.length === 0 && scanInfo && (
          <div className="bg-gray-800/30 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-16 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-700/50 rounded-full mb-6">
              <Clock className="w-10 h-10 text-gray-400" />
            </div>
            <p className="text-gray-300 text-xl font-semibold mb-2">
              No valid setups found with score &gt;= {minScore}
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
