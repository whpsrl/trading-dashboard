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
  { value: 'BTCUSDT', label: 'Bitcoin', type: 'crypto', icon: '₿' },
  { value: 'ETHUSDT', label: 'Ethereum', type: 'crypto', icon: 'Ξ' },
  { value: 'BNBUSDT', label: 'BNB', type: 'crypto', icon: '🔶' },
  { value: 'SOLUSDT', label: 'Solana', type: 'crypto', icon: '◎' },
  { value: 'XRPUSDT', label: 'Ripple', type: 'crypto', icon: '✕' },
  { value: 'ADAUSDT', label: 'Cardano', type: 'crypto', icon: '₳' },
  { value: 'DOGEUSDT', label: 'Dogecoin', type: 'crypto', icon: 'Ð' },
  { value: 'MATICUSDT', label: 'Polygon', type: 'crypto', icon: '⬡' },
  { value: 'DOTUSDT', label: 'Polkadot', type: 'crypto', icon: '●' },
  { value: 'LINKUSDT', label: 'Chainlink', type: 'crypto', icon: '⬢' },
];

const TIMEFRAMES = [
  { value: '15m', label: '15m' },
  { value: '1h', label: '1H' },
  { value: '4h', label: '4H' },
  { value: '1d', label: '1D' },
];

export default function ChartAnalyzer() {
  const [selectedSymbol, setSelectedSymbol] = useState(SYMBOLS[0]);
  const [selectedTimeframe, setSelectedTimeframe] = useState(TIMEFRAMES[1]);
  const [chartData, setChartData] = useState<OHLCVData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [aiPanelOpen, setAiPanelOpen] = useState(true);
  const [customPrompt, setCustomPrompt] = useState('');
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: {
        background: { color: '#0a0e17' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#1a1f2e' },
        horzLines: { color: '#1a1f2e' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: '#2962FF',
          width: 1,
          style: 1,
          labelBackgroundColor: '#2962FF',
        },
        horzLine: {
          color: '#2962FF',
          width: 1,
          style: 1,
          labelBackgroundColor: '#2962FF',
        },
      },
      rightPriceScale: {
        borderColor: '#1a1f2e',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
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
      
      console.log('🔍 Fetching:', endpoint);
      
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

  const analyzeWithAI = async (prompt: string) => {
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

      const fullPrompt = `Sei un analista tecnico esperto. Analizza i seguenti dati di mercato per ${selectedSymbol.label} sul timeframe ${selectedTimeframe.label}:

${JSON.stringify(marketContext, null, 2)}

Richiesta: ${prompt}

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

  const currentPrice = chartData[chartData.length - 1]?.close || 0;
  const prevPrice = chartData[chartData.length - 2]?.close || 0;
  const priceChange = currentPrice - prevPrice;
  const priceChangePercent = prevPrice ? (priceChange / prevPrice) * 100 : 0;

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0a0e17] to-[#0f1419] text-white overflow-hidden">
      
      {/* LEFT SIDEBAR - Symbols & Controls */}
      <div className="w-64 bg-[#0f1419] border-r border-gray-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            TradingDash Pro
          </h1>
          <p className="text-xs text-gray-500 mt-1">AI-Powered Analysis</p>
        </div>

        {/* Symbols List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="text-xs font-semibold text-gray-500 mb-2 px-2">CRYPTO MARKETS</div>
          {SYMBOLS.map((symbol) => (
            <button
              key={symbol.value}
              onClick={() => setSelectedSymbol(symbol)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                selectedSymbol.value === symbol.value
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/50'
                  : 'hover:bg-gray-800 text-gray-400'
              }`}
            >
              <span className="text-xl">{symbol.icon}</span>
              <div className="flex-1 text-left">
                <div className="text-sm font-medium">{symbol.label}</div>
                <div className="text-xs opacity-60">{symbol.value.replace('USDT', '/USDT')}</div>
              </div>
            </button>
          ))}
        </div>

        {/* Timeframes */}
        <div className="p-3 border-t border-gray-800">
          <div className="text-xs font-semibold text-gray-500 mb-2">TIMEFRAME</div>
          <div className="grid grid-cols-4 gap-1">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf.value}
                onClick={() => setSelectedTimeframe(tf)}
                className={`py-2 px-1 rounded-lg text-xs font-medium transition-all ${
                  selectedTimeframe.value === tf.value
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* CENTER - Chart Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="h-16 bg-[#0f1419] border-b border-gray-800 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-2xl">{selectedSymbol.icon}</span>
                <span className="text-xl font-bold">{selectedSymbol.label}</span>
                <span className="text-sm text-gray-500">{selectedTimeframe.label}</span>
              </div>
            </div>
            <div className="h-8 w-px bg-gray-700"></div>
            <div>
              <div className="text-2xl font-bold">
                ${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className={`text-sm ${priceChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {priceChangePercent >= 0 ? '▲' : '▼'} {Math.abs(priceChangePercent).toFixed(2)}%
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {loading && (
              <div className="flex items-center gap-2 text-blue-400">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-sm">Loading...</span>
              </div>
            )}
            {chartData.length > 0 && (
              <div className="text-xs text-gray-500">
                {chartData.length} candles
              </div>
            )}
            <button
              onClick={loadChartData}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Chart */}
        <div className="flex-1 relative">
          {error && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 px-4 py-2 bg-red-900/90 border border-red-700 rounded-lg text-red-200 text-sm">
              {error}
            </div>
          )}
          <div ref={chartContainerRef} className="w-full h-full" />
        </div>

        {/* Drawing Tools Bar (preparato per future implementazioni) */}
        <div className="h-14 bg-[#0f1419] border-t border-gray-800 flex items-center px-6 gap-3">
          <div className="text-xs text-gray-500 font-semibold">AI DRAWING TOOLS</div>
          <button className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg text-xs font-medium transition-all shadow-lg">
            🤖 Auto-Draw
          </button>
          <button className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs font-medium transition-all text-gray-400">
            🔺 Triangles
          </button>
          <button className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs font-medium transition-all text-gray-400">
            📈 Channels
          </button>
          <button className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs font-medium transition-all text-gray-400">
            🎯 Fibonacci
          </button>
          <div className="flex-1"></div>
          <button className="px-3 py-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg text-xs font-medium transition-all">
            🗑️ Clear All
          </button>
        </div>
      </div>

      {/* RIGHT PANEL - AI Analysis */}
      <div className={`bg-[#0f1419] border-l border-gray-800 transition-all duration-300 flex flex-col ${aiPanelOpen ? 'w-96' : 'w-12'}`}>
        {/* Toggle Button */}
        <button
          onClick={() => setAiPanelOpen(!aiPanelOpen)}
          className="h-16 border-b border-gray-800 flex items-center justify-center hover:bg-gray-800 transition-colors"
        >
          <span className="text-xl">{aiPanelOpen ? '→' : '←'}</span>
        </button>

        {aiPanelOpen && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* AI Panel Header */}
            <div className="p-4 border-b border-gray-800">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <span>🤖</span> AI Analysis
              </h3>
              <p className="text-xs text-gray-500 mt-1">Claude Sonnet 4</p>
            </div>

            {/* Preset Buttons */}
            <div className="p-4 border-b border-gray-800 space-y-2">
              <div className="text-xs font-semibold text-gray-500 mb-2">QUICK ANALYSIS</div>
              <button
                onClick={() => analyzeWithAI('Analizza i pattern candlestick e identifica formazioni importanti')}
                disabled={analyzing || !chartData.length}
                className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-800 disabled:text-gray-600 rounded-lg text-sm font-medium transition-all text-left"
              >
                📊 Pattern Recognition
              </button>
              <button
                onClick={() => analyzeWithAI('Identifica livelli di supporto e resistenza chiave')}
                disabled={analyzing || !chartData.length}
                className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-800 disabled:text-gray-600 rounded-lg text-sm font-medium transition-all text-left"
              >
                📏 Support/Resistance
              </button>
              <button
                onClick={() => analyzeWithAI('Analizza trend e possibili inversioni')}
                disabled={analyzing || !chartData.length}
                className="w-full px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-800 disabled:text-gray-600 rounded-lg text-sm font-medium transition-all text-left"
              >
                📈 Trend Analysis
              </button>
              <button
                onClick={() => analyzeWithAI('Identifica zone di imbalance/FVG e gap significativi')}
                disabled={analyzing || !chartData.length}
                className="w-full px-3 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-800 disabled:text-gray-600 rounded-lg text-sm font-medium transition-all text-left"
              >
                🟢 Imbalance Zones
              </button>
            </div>

            {/* Custom Prompt */}
            <div className="p-4 border-b border-gray-800">
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Custom analysis request..."
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm resize-none focus:outline-none focus:border-blue-500 transition-colors"
                rows={3}
              />
              <button
                onClick={() => analyzeWithAI(customPrompt)}
                disabled={analyzing || !customPrompt.trim() || !chartData.length}
                className="w-full mt-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-800 disabled:to-gray-800 disabled:text-gray-600 rounded-lg text-sm font-medium transition-all"
              >
                {analyzing ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>

            {/* AI Response */}
            <div className="flex-1 overflow-y-auto p-4">
              {aiResponse ? (
                <div className="space-y-3">
                  {aiResponse.split('\n\n').map((block, idx) => {
                    const lines = block.split('\n').filter(l => l.trim());
                    if (lines.length === 0) return null;
                    
                    const firstLine = lines[0];
                    
                    if (firstLine.startsWith('##')) {
                      const title = firstLine.replace(/^##\s*/, '').replace(/📊|🕯️|📈|⚠️|📋|🎯|🟢|🔴/g, '').trim();
                      const icon = firstLine.match(/📊|🕯️|📈|⚠️|📋|🎯|🟢|🔴/)?.[0] || '📊';
                      
                      return (
                        <div key={idx} className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-800">
                            <span className="text-xl">{icon}</span>
                            <h4 className="font-bold text-sm">{title}</h4>
                          </div>
                          <div className="space-y-2 text-xs text-gray-300">
                            {lines.slice(1).map((line, i) => {
                              if (line.startsWith('###')) {
                                return <div key={i} className="font-semibold text-green-400 mt-2">{line.replace(/^###\s*/, '')}</div>;
                              }
                              if (line.includes('**') && line.includes(':')) {
                                const match = line.match(/\*\*([^*]+)\*\*:\s*(.+)/);
                                if (match) {
                                  return (
                                    <div key={i} className="flex gap-2">
                                      <span className="font-semibold text-yellow-400">{match[1]}:</span>
                                      <span>{match[2]}</span>
                                    </div>
                                  );
                                }
                              }
                              if (line.trim().startsWith('-')) {
                                return <div key={i} className="ml-3">• {line.replace(/^-\s*/, '')}</div>;
                              }
                              return <div key={i}>{line}</div>;
                            })}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-600 text-sm text-center">
                  {analyzing ? (
                    <div className="space-y-3">
                      <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                      <div>Analyzing chart...</div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="text-4xl">🤖</div>
                      <div>Select an analysis<br />or enter custom prompt</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
