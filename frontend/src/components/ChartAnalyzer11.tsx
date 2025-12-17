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
  // Crypto
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
  // Forex
  { value: 'GBPJPY', label: 'GBP/JPY', type: 'forex' },
  { value: 'EURUSD', label: 'EUR/USD', type: 'forex' },
  { value: 'USDJPY', label: 'USD/JPY', type: 'forex' },
  { value: 'GBPUSD', label: 'GBP/USD', type: 'forex' },
  { value: 'AUDUSD', label: 'AUD/USD', type: 'forex' },
  // Stocks
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
      height: 500,
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
      const endpoint = `${apiUrl}/api/v1/market-data/${selectedSymbol.type}/${selectedSymbol.value}?timeframe=${selectedTimeframe.value}&limit=500`;
      
      console.log('🔍 Fetching from:', endpoint);
      
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📦 Response:', data);
      
      // Try different response formats
      let rawData = data.data || data.candles || data.ohlcv || data;
      
      if (!Array.isArray(rawData)) {
        console.error('❌ Not an array:', rawData);
        throw new Error('Invalid response format');
      }
      
      console.log(`✅ Got ${rawData.length} candles`);
      
      if (rawData.length === 0) {
        throw new Error('No data available');
      }
      
      console.log('📌 Sample candle:', rawData[0]);
      
      const formattedData: OHLCVData[] = rawData.map((item: any) => {
        // Handle different timestamp formats
        let timestamp;
        if (item.timestamp) {
          timestamp = new Date(item.timestamp).getTime() / 1000;
        } else if (item.time) {
          timestamp = typeof item.time === 'number' ? item.time : new Date(item.time).getTime() / 1000;
        } else if (Array.isArray(item) && item.length >= 6) {
          // [timestamp, open, high, low, close, volume]
          timestamp = item[0] / 1000;
        } else {
          throw new Error('Cannot find timestamp in data');
        }
        
        return {
          time: timestamp as UTCTimestamp,
          open: parseFloat(item.open || item[1] || 0),
          high: parseFloat(item.high || item[2] || 0),
          low: parseFloat(item.low || item[3] || 0),
          close: parseFloat(item.close || item[4] || 0),
          volume: parseFloat(item.volume || item[5] || 0),
        };
      });
      
      // Sort by time
      formattedData.sort((a, b) => a.time - b.time);
      
      console.log('✨ Formatted:', formattedData.slice(0, 2));
      
      setChartData(formattedData);
      
      if (candlestickSeriesRef.current && formattedData.length > 0) {
        candlestickSeriesRef.current.setData(formattedData);
        console.log('🎨 Chart updated!');
      }
      
    } catch (err: any) {
      console.error('❌ Error:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const analyzeWithAI = async (customPrompt?: string) => {
    if (!chartData.length) {
      alert('Carica prima i dati del grafico');
      return;
    }

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
        recentCandles: chartData.slice(-20).map(d => ({
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

Richiesta dell'utente: ${userPrompt}

Fornisci un'analisi dettagliata, professionale e actionable.`;

      const response = await fetch(`${apiUrl}/api/v1/ai/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: fullPrompt,
        }),
      });

      const result = await response.json();
      setAiResponse(result.analysis || result.message || 'Nessuna risposta dall\'AI');
    } catch (error) {
      console.error('Error analyzing:', error);
      setAiResponse('Errore durante l\'analisi. Verifica che il backend sia online.');
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    loadChartData();
  }, [selectedSymbol, selectedTimeframe]);

  return (
    <div className="flex flex-col gap-6 p-6 bg-gray-900 min-h-screen">
      <div className="flex flex-col gap-4 bg-gray-800 p-6 rounded-lg">
        <h1 className="text-3xl font-bold text-white">Chart Analyzer</h1>
        
        <div className="flex gap-4 flex-wrap">
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">Symbol</label>
            <select
              value={selectedSymbol.value}
              onChange={(e) => setSelectedSymbol(SYMBOLS.find(s => s.value === e.target.value)!)}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              {SYMBOLS.map((sym) => (
                <option key={sym.value} value={sym.value}>
                  {sym.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">Timeframe</label>
            <select
              value={selectedTimeframe.value}
              onChange={(e) => setSelectedTimeframe(TIMEFRAMES.find(t => t.value === e.target.value)!)}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              {TIMEFRAMES.map((tf) => (
                <option key={tf.value} value={tf.value}>
                  {tf.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadChartData}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
            >
              {loading ? 'Loading...' : 'Refresh Chart'}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="px-4 py-3 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
            ❌ {error}
          </div>
        )}
        
        {chartData.length > 0 && (
          <div className="text-sm text-gray-400">
            ✅ Loaded {chartData.length} candles
          </div>
        )}
      </div>

      <div className="bg-gray-800 p-4 rounded-lg">
        <div ref={chartContainerRef} className="w-full" style={{ minHeight: '500px' }} />
      </div>

      <div className="flex flex-col gap-4 bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-bold text-white">AI Analysis</h2>
        
        <div className="flex gap-2 flex-wrap">
          {PRESET_PROMPTS.map((preset) => (
            <button
              key={preset.label}
              onClick={() => {
                setPrompt(preset.prompt);
                analyzeWithAI(preset.prompt);
              }}
              disabled={analyzing || !chartData.length}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm text-gray-400">Custom Analysis Request</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Es: Analizza il doppio massimo che vedo sul grafico..."
            className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            rows={3}
          />
          <button
            onClick={() => analyzeWithAI()}
            disabled={analyzing || !prompt.trim() || !chartData.length}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            {analyzing ? 'Analyzing...' : 'Analyze Chart'}
          </button>
        </div>

        {aiResponse && (
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400 font-semibold mb-2">AI Analysis Result</label>
            <div className="space-y-4">
              {aiResponse.split('\n\n').map((block, blockIdx) => {
                const lines = block.split('\n').filter(l => l.trim());
                if (lines.length === 0) return null;
                
                const firstLine = lines[0];
                
                // Detect section type by header
                if (firstLine.startsWith('##')) {
                  const title = firstLine.replace(/^##\s*/, '').replace(/📊|🕯️|📈|⚠️|📋|🎯|🔴|🟢|🟡/g, '').trim();
                  const icon = firstLine.match(/📊|🕯️|📈|⚠️|📋|🎯|🔴|🟢|🟡/)?.[0] || '📊';
                  
                  const getBgColor = () => {
                    if (title.includes('BULLISH') || title.includes('SCENARI')) return 'from-green-900/30 to-green-800/20 border-green-700/50';
                    if (title.includes('BEARISH')) return 'from-red-900/30 to-red-800/20 border-red-700/50';
                    if (title.includes('OVERVIEW') || title.includes('MERCATO')) return 'from-blue-900/30 to-blue-800/20 border-blue-700/50';
                    if (title.includes('PATTERN') || title.includes('CANDLESTICK')) return 'from-yellow-900/30 to-yellow-800/20 border-yellow-700/50';
                    if (title.includes('VOLUME')) return 'from-purple-900/30 to-purple-800/20 border-purple-700/50';
                    if (title.includes('LIVELLI') || title.includes('SUPPORTO')) return 'from-orange-900/30 to-orange-800/20 border-orange-700/50';
                    return 'from-gray-800 to-gray-900 border-gray-700';
                  };
                  
                  return (
                    <div key={blockIdx} className={`bg-gradient-to-br ${getBgColor()} rounded-xl border p-5 shadow-lg`}>
                      {/* Header */}
                      <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-700/50">
                        <span className="text-3xl">{icon}</span>
                        <h2 className="text-xl font-bold text-white">{title}</h2>
                      </div>
                      
                      {/* Content */}
                      <div className="space-y-3">
                        {lines.slice(1).map((line, lineIdx) => {
                          // Sub-headers
                          if (line.startsWith('###')) {
                            return (
                              <h3 key={lineIdx} className="text-lg font-semibold text-green-400 mt-4 mb-2 flex items-center gap-2">
                                <span className="text-green-500">▶</span>
                                {line.replace(/^###\s*/, '').replace(/\*\*/g, '')}
                              </h3>
                            );
                          }
                          
                          if (line.startsWith('####')) {
                            return (
                              <h4 key={lineIdx} className="text-base font-medium text-purple-300 mt-2 ml-2 flex items-center gap-2">
                                <span className="text-purple-400">•</span>
                                {line.replace(/^####\s*/, '').replace(/\*\*/g, '')}
                              </h4>
                            );
                          }
                          
                          // Key-value pairs (bold: value)
                          if (line.includes('**') && line.includes(':')) {
                            const match = line.match(/\*\*([^*]+)\*\*:\s*(.+)/);
                            if (match) {
                              return (
                                <div key={lineIdx} className="flex items-start gap-3 p-3 bg-gray-800/40 rounded-lg">
                                  <span className="font-bold text-yellow-400 min-w-[160px]">{match[1]}:</span>
                                  <span className="text-gray-200 flex-1">{match[2]}</span>
                                </div>
                              );
                            }
                          }
                          
                          // List items
                          if (line.trim().startsWith('-')) {
                            return (
                              <div key={lineIdx} className="flex items-start gap-2 ml-4">
                                <span className="text-blue-400 mt-1 font-bold">•</span>
                                <p className="text-gray-300 flex-1">{line.replace(/^-\s*/, '').replace(/\*\*/g, '')}</p>
                              </div>
                            );
                          }
                          
                          // Regular text
                          if (line.trim()) {
                            return (
                              <p key={lineIdx} className="text-gray-300 leading-relaxed">
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
              
              {/* Warning footer */}
              <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-700/50 rounded-lg flex items-center gap-3">
                <span className="text-2xl">⚠️</span>
                <p className="text-yellow-200 text-sm">
                  <strong>Disclaimer:</strong> Questa analisi AI è solo a scopo informativo e non costituisce consulenza finanziaria. 
                  Fai sempre le tue ricerche prima di investire.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
