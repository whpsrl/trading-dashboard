// NOTA: Questo file sostituisce completamente ChartAnalyzer.tsx
// È la versione FINALE con:
// - Layout 2 colonne: Chart 65% + AI Panel 35% 
// - Restyling premium con colori moderni
// - 1000 candele
// - Box risultati scrollabile separato

'use client';

import { useState, useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, UTCTimestamp } from 'lightweight-charts';

interface OHLCVData {
  time: UTCTimestamp;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const SYMBOLS = [
  { value: 'BTCUSDT', label: 'Bitcoin (BTC/USDT)', type: 'crypto' },
  { value: 'ETHUSDT', label: 'Ethereum (ETH/USDT)', type: 'crypto' },
  { value: 'BNBUSDT', label: 'Binance Coin (BNB/USDT)', type: 'crypto' },
  { value: 'SOLUSDT', label: 'Solana (SOL/USDT)', type: 'crypto' },
  { value: 'XRPUSDT', label: 'Ripple (XRP/USDT)', type: 'crypto' },
  { value: 'ADAUSDT', label: 'Cardano (ADA/USDT)', type: 'crypto' },
  { value: 'DOGEUSDT', label: 'Dogecoin (DOGE/USDT)', type: 'crypto' },
  { value: 'MATICUSDT', label: 'Polygon (MATIC/USDT)', type: 'crypto' },
  { value: 'DOTUSDT', label: 'Polkadot (DOT/USDT)', type: 'crypto' },
  { value: 'LINKUSDT', label: 'Chainlink (LINK/USDT)', type: 'crypto' },
  { value: 'GBPJPY', label: 'GBP/JPY', type: 'forex' },
  { value: 'EURUSD', label: 'EUR/USD', type: 'forex' },
  { value: 'USDJPY', label: 'USD/JPY', type: 'forex' },
  { value: 'GBPUSD', label: 'GBP/USD', type: 'forex' },
  { value: 'AUDUSD', label: 'AUD/USD', type: 'forex' },
  { value: 'AAPL', label: 'Apple', type: 'stock' },
  { value: 'GOOGL', label: 'Google', type: 'stock' },
  { value: 'MSFT', label: 'Microsoft', type: 'stock' },
  { value: 'TSLA', label: 'Tesla', type: 'stock' },
  { value: 'AMZN', label: 'Amazon', type: 'stock' },
  { value: 'NVDA', label: 'NVIDIA', type: 'stock' },
  { value: 'META', label: 'Meta', type: 'stock' },
];

const TIMEFRAMES = [
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
];

const PRESET_PROMPTS = [
  { label: 'Pattern Recognition', prompt: 'Analizza i pattern candlestick presenti nel grafico e identifica formazioni importanti' },
  { label: 'Support/Resistance', prompt: 'Identifica i livelli di supporto e resistenza chiave basandoti sui dati storici' },
  { label: 'Trend Analysis', prompt: 'Analizza il trend principale e identifica possibili inversioni o continuazioni' },
  { label: 'Volume Analysis', prompt: 'Analizza il volume degli scambi e correla con i movimenti di prezzo' },
];

export default function ChartAnalyzer() {
  const [selectedSymbol, setSelectedSymbol] = useState(SYMBOLS[0]);
  const [selectedTimeframe, setSelectedTimeframe] = useState(TIMEFRAMES[0]);
  const [chartData, setChartData] = useState<OHLCVData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [prompt, setPrompt] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: {
        background: { color: '#0a0e17' },
        textColor: '#8b9bb8',
      },
      grid: {
        vertLines: { color: '#1a1f2e' },
        horzLines: { color: '#1a1f2e' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#1a1f2e',
      },
      timeScale: {
        borderColor: '#1a1f2e',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  const loadChartData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endpoint = `${apiUrl}/api/v1/market-data/${selectedSymbol.type}/${selectedSymbol.value}?timeframe=${selectedTimeframe.value}&limit=1000`;
      
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      let rawData = data.data || data.candles || data;
      
      if (!Array.isArray(rawData) || rawData.length === 0) {
        throw new Error('No data available');
      }
      
      const formattedData: OHLCVData[] = rawData.map((item: any) => {
        let timestamp;
        if (item.timestamp) {
          timestamp = new Date(item.timestamp).getTime() / 1000;
        } else if (item.time) {
          timestamp = typeof item.time === 'number' ? item.time : new Date(item.time).getTime() / 1000;
        } else if (Array.isArray(item)) {
          timestamp = item[0] / 1000;
        }
        
        return {
          time: timestamp as UTCTimestamp,
          open: parseFloat(item.open || item[1]),
          high: parseFloat(item.high || item[2]),
          low: parseFloat(item.low || item[3]),
          close: parseFloat(item.close || item[4]),
          volume: parseFloat(item.volume || item[5] || 0),
        };
      });
      
      formattedData.sort((a, b) => a.time - b.time);
      setChartData(formattedData);
      
      if (candlestickSeriesRef.current && formattedData.length > 0) {
        candlestickSeriesRef.current.setData(formattedData);
      }
      
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const analyzeWithAI = async (customPrompt?: string) => {
    if (!chartData.length) return;

    setAnalyzing(true);
    setAiResponse('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const marketContext = {
        symbol: selectedSymbol.label,
        timeframe: selectedTimeframe.label,
        dataPoints: chartData.length,
        currentPrice: chartData[chartData.length - 1]?.close,
        priceRange: {
          high: Math.max(...chartData.map(d => d.high)),
          low: Math.min(...chartData.map(d => d.low)),
        },
        recentCandles: chartData.slice(-50).map(d => ({
          time: new Date(d.time * 1000).toISOString(),
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          volume: d.volume,
        })),
      };

      const userPrompt = customPrompt || prompt;
      const fullPrompt = `Sei un analista tecnico esperto. Analizza i seguenti dati di mercato per ${selectedSymbol.label} sul timeframe ${selectedTimeframe.label}:

${JSON.stringify(marketContext, null, 2)}

Richiesta: ${userPrompt}

Fornisci un'analisi dettagliata, professionale e actionable con sezioni ben organizzate usando headers ##, ### e ####.`;

      const response = await fetch(`${apiUrl}/api/v1/ai/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: fullPrompt }),
      });

      const result = await response.json();
      setAiResponse(result.analysis || 'Nessuna risposta');
    } catch (error) {
      setAiResponse('Errore durante l\'analisi');
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    loadChartData();
  }, [selectedSymbol, selectedTimeframe]);

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      
      {/* Top Bar */}
      <div className="flex gap-4 items-center bg-slate-900/90 backdrop-blur-xl px-6 py-4 border-b border-cyan-900/20 shadow-2xl shrink-0">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-transparent">
          Chart Analyzer Pro
        </h1>
        
        <div className="h-8 w-px bg-cyan-800/30"></div>
        
        <select
          value={selectedSymbol.value}
          onChange={(e) => setSelectedSymbol(SYMBOLS.find(s => s.value === e.target.value)!)}
          className="px-4 py-2 bg-slate-800/60 backdrop-blur text-cyan-100 rounded-lg border border-cyan-800/20 hover:border-cyan-600/40 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 focus:outline-none transition-all text-sm font-medium shadow-lg"
        >
          {SYMBOLS.map((sym) => (
            <option key={sym.value} value={sym.value} className="bg-slate-900">{sym.label}</option>
          ))}
        </select>

        <select
          value={selectedTimeframe.value}
          onChange={(e) => setSelectedTimeframe(TIMEFRAMES.find(t => t.value === e.target.value)!)}
          className="px-4 py-2 bg-slate-800/60 backdrop-blur text-cyan-100 rounded-lg border border-cyan-800/20 hover:border-cyan-600/40 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 focus:outline-none transition-all text-sm font-medium shadow-lg"
        >
          {TIMEFRAMES.map((tf) => (
            <option key={tf.value} value={tf.value} className="bg-slate-900">{tf.label}</option>
          ))}
        </select>

        <button
          onClick={loadChartData}
          disabled={loading}
          className="px-5 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:from-slate-700 disabled:to-slate-600 text-white rounded-lg font-semibold transition-all text-sm shadow-lg hover:shadow-cyan-500/30"
        >
          {loading ? '⏳' : '🔄'} {loading ? 'Loading' : 'Refresh'}
        </button>
        
        <div className="flex-1"></div>
        
        {chartData.length > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-900/20 border border-emerald-700/20 rounded-lg backdrop-blur">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
            <span className="text-emerald-300 text-sm font-medium">{chartData.length} candles</span>
          </div>
        )}
        
        {error && (
          <div className="px-3 py-1.5 bg-red-900/20 border border-red-700/20 rounded-lg text-red-300 text-xs backdrop-blur">
            {error}
          </div>
        )}
      </div>

      {/* Main: 2 Columns */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* LEFT: Chart (65%) */}
        <div className="flex-1 p-6" style={{ width: '65%' }}>
          <div className="w-full h-full rounded-2xl overflow-hidden border border-cyan-900/20 shadow-2xl shadow-cyan-900/10 bg-slate-900/30 backdrop-blur">
            <div ref={chartContainerRef} className="w-full h-full" />
          </div>
        </div>

        {/* RIGHT: AI Panel (35%) */}
        <div className="flex flex-col bg-slate-900/50 backdrop-blur border-l border-cyan-900/20" style={{ width: '35%' }}>
          
          {/* AI Controls - Fixed */}
          <div className="p-5 space-y-4 border-b border-cyan-900/20 shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                <span className="text-2xl">🤖</span>
              </div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                AI Analysis
              </h2>
            </div>
            
            {/* Preset Buttons */}
            <div className="space-y-2">
              {PRESET_PROMPTS.map((preset, idx) => {
                const colors = [
                  'from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500',
                  'from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500',
                  'from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500',
                  'from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500',
                ];
                return (
                  <button
                    key={preset.label}
                    onClick={() => {
                      setPrompt(preset.prompt);
                      analyzeWithAI(preset.prompt);
                    }}
                    disabled={analyzing || !chartData.length}
                    className={`w-full px-4 py-2.5 bg-gradient-to-r ${colors[idx]} disabled:from-slate-800 disabled:to-slate-700 disabled:text-slate-500 text-white rounded-xl text-sm font-semibold transition-all text-left shadow-lg hover:scale-[1.02] active:scale-[0.98]`}
                  >
                    {preset.label}
                  </button>
                );
              })}
            </div>

            {/* Custom Prompt */}
            <div className="space-y-2">
              <label className="text-sm font-semibold text-cyan-400">Custom Request</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ask anything about the chart..."
                className="w-full px-4 py-3 bg-slate-800/50 backdrop-blur text-cyan-50 placeholder-slate-500 rounded-xl border border-cyan-800/20 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 focus:outline-none resize-none text-sm shadow-inner"
                rows={3}
              />
              <button
                onClick={() => analyzeWithAI()}
                disabled={analyzing || !prompt.trim() || !chartData.length}
                className="w-full px-4 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:from-slate-800 disabled:to-slate-700 disabled:text-slate-500 text-white rounded-xl font-semibold transition-all text-sm shadow-lg"
              >
                {analyzing ? '⚡ Analyzing...' : '✨ Analyze'}
              </button>
            </div>
          </div>

          {/* AI Results - Scrollable */}
          <div className="flex-1 overflow-y-auto bg-slate-950/70 p-4">
            <div className="space-y-3">
              
              {analyzing && (
                <div className="text-center py-20">
                  <div className="relative w-16 h-16 mx-auto mb-4">
                    <div className="absolute inset-0 border-4 border-cyan-600/20 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-transparent border-t-cyan-500 rounded-full animate-spin"></div>
                  </div>
                  <div className="text-cyan-400 font-semibold mb-1">Analyzing...</div>
                  <div className="text-slate-500 text-sm">Claude is thinking</div>
                </div>
              )}

              {!aiResponse && !analyzing && (
                <div className="text-center py-20">
                  <div className="text-7xl mb-4 opacity-40">🤖</div>
                  <div className="text-cyan-400 font-semibold mb-1">Ready to analyze</div>
                  <div className="text-slate-500 text-sm">Select preset or custom prompt</div>
                </div>
              )}

              {aiResponse && !analyzing && (
                <>
                  <div className="flex items-center gap-2 mb-4 sticky top-0 bg-slate-950/90 backdrop-blur py-2 z-10 border-b border-cyan-900/20">
                    <div className="w-1 h-5 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
                    <span className="text-sm font-bold text-cyan-400">Analysis Result</span>
                  </div>
                  
                  {aiResponse.split('\n\n').map((block, blockIdx) => {
                    const lines = block.split('\n').filter(l => l.trim());
                    if (lines.length === 0) return null;
                    
                    const firstLine = lines[0];
                    
                    if (firstLine.startsWith('##')) {
                      const title = firstLine.replace(/^##\s*/, '').replace(/📊|🕯️|📈|⚠️|📋|🎯|🔴|🟢|🟡/g, '').trim();
                      const icon = firstLine.match(/📊|🕯️|📈|⚠️|📋|🎯|🔴|🟢|🟡/)?.[0] || '📊';
                      
                      const getCardStyle = () => {
                        if (title.includes('BULLISH')) return { bg: 'from-emerald-950/60 to-green-900/30', border: 'border-emerald-700/30', shadow: 'shadow-emerald-500/10' };
                        if (title.includes('BEARISH')) return { bg: 'from-red-950/60 to-rose-900/30', border: 'border-red-700/30', shadow: 'shadow-red-500/10' };
                        if (title.includes('OVERVIEW')) return { bg: 'from-blue-950/60 to-cyan-900/30', border: 'border-blue-700/30', shadow: 'shadow-blue-500/10' };
                        if (title.includes('PATTERN')) return { bg: 'from-amber-950/60 to-yellow-900/30', border: 'border-amber-700/30', shadow: 'shadow-amber-500/10' };
                        if (title.includes('VOLUME')) return { bg: 'from-purple-950/60 to-violet-900/30', border: 'border-purple-700/30', shadow: 'shadow-purple-500/10' };
                        if (title.includes('LIVELLI')) return { bg: 'from-orange-950/60 to-red-900/30', border: 'border-orange-700/30', shadow: 'shadow-orange-500/10' };
                        return { bg: 'from-slate-900/60 to-slate-800/30', border: 'border-slate-700/30', shadow: 'shadow-slate-500/10' };
                      };
                      
                      const style = getCardStyle();
                      
                      return (
                        <div key={blockIdx} className={`bg-gradient-to-br ${style.bg} backdrop-blur rounded-xl border ${style.border} p-4 shadow-xl ${style.shadow} hover:scale-[1.01] transition-transform`}>
                          <div className="flex items-center gap-2.5 mb-3 pb-2.5 border-b border-cyan-900/20">
                            <span className="text-2xl">{icon}</span>
                            <h3 className="text-base font-bold text-cyan-100">{title}</h3>
                          </div>
                          
                          <div className="space-y-2.5 text-xs leading-relaxed">
                            {lines.slice(1).map((line, lineIdx) => {
                              if (line.startsWith('###')) {
                                return (
                                  <div key={lineIdx} className="font-bold text-emerald-400 mt-3 flex items-center gap-2">
                                    <span className="text-emerald-500">▶</span>
                                    <span>{line.replace(/^###\s*/, '').replace(/\*\*/g, '')}</span>
                                  </div>
                                );
                              }
                              
                              if (line.startsWith('####')) {
                                return (
                                  <div key={lineIdx} className="font-semibold text-purple-300 ml-4 flex items-center gap-2 mt-2">
                                    <span className="text-purple-400">•</span>
                                    <span>{line.replace(/^####\s*/, '').replace(/\*\*/g, '')}</span>
                                  </div>
                                );
                              }
                              
                              if (line.includes('**') && line.includes(':')) {
                                const match = line.match(/\*\*([^*]+)\*\*:\s*(.+)/);
                                if (match) {
                                  return (
                                    <div key={lineIdx} className="flex gap-2.5 p-2.5 bg-slate-900/50 backdrop-blur rounded-lg border border-cyan-900/10">
                                      <span className="font-bold text-cyan-400 shrink-0 min-w-[100px]">{match[1]}:</span>
                                      <span className="text-slate-200">{match[2]}</span>
                                    </div>
                                  );
                                }
                              }
                              
                              if (line.trim().startsWith('-')) {
                                return (
                                  <div key={lineIdx} className="flex gap-2 ml-4 items-start">
                                    <span className="text-cyan-500 mt-0.5">•</span>
                                    <span className="text-slate-300">{line.replace(/^-\s*/, '').replace(/\*\*/g, '')}</span>
                                  </div>
                                );
                              }
                              
                              if (line.trim()) {
                                return (
                                  <p key={lineIdx} className="text-slate-300">
                                    {line.replace(/\*\*/g, '')}
                                  </p>
                                );
                              }
                              
                              return null;
                            })}
                          </div>
                        </div>
                      );
                    }
                    
                    return null;
                  })}
                  
                  <div className="mt-5 p-3.5 bg-amber-900/20 border border-amber-700/30 rounded-xl flex gap-3 backdrop-blur">
                    <span className="text-2xl">⚠️</span>
                    <p className="text-amber-200 text-xs leading-relaxed">
                      <strong className="text-amber-100">Disclaimer:</strong> Questa analisi AI è solo a scopo informativo e non costituisce consulenza finanziaria.
                    </p>
                  </div>
                </>
              )}

            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
