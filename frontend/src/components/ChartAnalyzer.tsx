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
      height: 600,
      layout: {
        background: { color: '#1a1a1a' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2a2a2a' },
        horzLines: { color: '#2a2a2a' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#2a2a2a',
      },
      timeScale: {
        borderColor: '#2a2a2a',
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
    <div className="flex flex-row h-screen w-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 overflow-hidden">
      
      {/* LEFT: Chart + Controls */}
      <div className="flex flex-col shrink-0" style={{ width: '65%', minWidth: '65%', maxWidth: '65%' }}>
        
        {/* Top Controls */}
        <div className="flex gap-4 items-center bg-slate-800/80 backdrop-blur p-4 border-b border-blue-900/30 shrink-0">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Chart Analyzer</h1>
          
          <select
            value={selectedSymbol.value}
            onChange={(e) => setSelectedSymbol(SYMBOLS.find(s => s.value === e.target.value)!)}
            className="px-4 py-2 bg-slate-700 text-white rounded-lg border border-blue-600 focus:border-blue-500 focus:outline-none"
          >
            {SYMBOLS.map((sym) => (
              <option key={sym.value} value={sym.value}>{sym.label}</option>
            ))}
          </select>

          <select
            value={selectedTimeframe.value}
            onChange={(e) => setSelectedTimeframe(TIMEFRAMES.find(t => t.value === e.target.value)!)}
            className="px-4 py-2 bg-slate-700 text-white rounded-lg border border-blue-600 focus:border-blue-500 focus:outline-none"
          >
            {TIMEFRAMES.map((tf) => (
              <option key={tf.value} value={tf.value}>{tf.label}</option>
            ))}
          </select>

          <button
            onClick={loadChartData}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          
          {chartData.length > 0 && (
            <div className="text-sm text-green-400 ml-auto">✓ {chartData.length} candles</div>
          )}
          
          {error && (
            <div className="text-sm text-red-400">{error}</div>
          )}
        </div>

        {/* Chart */}
        <div className="flex-1 bg-slate-900 p-4">
          <div ref={chartContainerRef} className="w-full h-full rounded-lg border border-blue-900/30" />
        </div>
      </div>

      {/* RIGHT: AI Panel */}
      <div className="flex flex-col bg-slate-900/80 backdrop-blur border-l border-blue-900/30 shrink-0" style={{ width: '35%', minWidth: '35%', maxWidth: '35%' }}>
        
        {/* AI Controls */}
        <div className="p-4 space-y-4 border-b border-blue-900/30">
          <h2 className="text-xl font-bold text-blue-400">🤖 AI Analysis</h2>
          
          <div className="space-y-2">
            {PRESET_PROMPTS.map((preset) => (
              <button
                key={preset.label}
                onClick={() => {
                  setPrompt(preset.prompt);
                  analyzeWithAI(preset.prompt);
                }}
                disabled={analyzing || !chartData.length}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white rounded-lg text-sm font-medium transition-colors text-left"
              >
                {preset.label}
              </button>
            ))}
          </div>

          <div className="space-y-2">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Custom analysis request..."
              className="w-full px-3 py-2 bg-slate-800 text-white rounded-lg border border-blue-700 focus:border-blue-500 focus:outline-none resize-none text-sm"
              rows={3}
            />
            <button
              onClick={() => analyzeWithAI()}
              disabled={analyzing || !prompt.trim() || !chartData.length}
              className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white rounded-lg font-medium transition-colors text-sm"
            >
              {analyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        {/* AI Results - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 bg-slate-950">
          {analyzing && (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <div className="text-blue-400">Analyzing...</div>
            </div>
          )}

          {!aiResponse && !analyzing && (
            <div className="text-center py-12 text-gray-500">
              <div className="text-5xl mb-2">🤖</div>
              <div>Select an analysis</div>
            </div>
          )}

          {aiResponse && (
            <div className="space-y-4 text-sm text-gray-300">
              {aiResponse.split('\n\n').map((block, idx) => {
                if (block.startsWith('##')) {
                  return (
                    <div key={idx} className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-4">
                      <h3 className="text-blue-400 font-bold mb-2">{block.replace(/^##\s*/, '')}</h3>
                    </div>
                  );
                }
                return (
                  <div key={idx} className="leading-relaxed">
                    {block}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
