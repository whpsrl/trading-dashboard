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
  { value: 'GBP_JPY', label: 'GBP/JPY', type: 'forex' },
  { value: 'EUR_USD', label: 'EUR/USD', type: 'forex' },
  { value: 'GOOGL', label: 'Google', type: 'stock' },
  { value: 'AAPL', label: 'Apple', type: 'stock' },
];

const TIMEFRAMES = [
  { value: '1m', label: '1 Minute' },
  { value: '5m', label: '5 Minutes' },
  { value: '15m', label: '15 Minutes' },
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
  const [selectedTimeframe, setSelectedTimeframe] = useState(TIMEFRAMES[2]); // 15m default
  const [chartData, setChartData] = useState<OHLCVData[]>([]);
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

  // Inizializza il grafico
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

  // Carica dati dal backend
  const loadChartData = async () => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endpoint = `${apiUrl}/api/v1/market-data/${selectedSymbol.type}/${selectedSymbol.value}?timeframe=${selectedTimeframe.value}&limit=200`;
      
      console.log('🔍 Fetching:', endpoint);
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📦 Backend response:', data);
      console.log('📊 Data keys:', Object.keys(data));
      
      // Handle different response formats
      let ohlcvArray = data.data || data.candles || data;
      
      if (!Array.isArray(ohlcvArray)) {
        console.error('❌ Data is not array:', typeof ohlcvArray);
        throw new Error('Invalid data format from backend');
      }
      
      console.log(`✅ Found ${ohlcvArray.length} candles`);
      
      if (ohlcvArray.length > 0) {
        console.log('📌 First candle:', ohlcvArray[0]);
      }
      
      const formattedData: OHLCVData[] = ohlcvArray.map((item: any) => ({
        time: (new Date(item.timestamp || item.time || item[0]).getTime() / 1000) as UTCTimestamp,
        open: parseFloat(item.open || item[1]),
        high: parseFloat(item.high || item[2]),
        low: parseFloat(item.low || item[3]),
        close: parseFloat(item.close || item[4]),
        volume: parseFloat(item.volume || item[5] || 0),
      }));
      
      console.log('✨ Formatted data:', formattedData.slice(0, 2));
      
      setChartData(formattedData);
      
      if (candlestickSeriesRef.current) {
        candlestickSeriesRef.current.setData(formattedData);
        console.log('🎨 Chart updated with data!');
      }
    } catch (error) {
      console.error('❌ Error loading chart data:', error);
      alert(`Failed to load chart: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  // Analizza con AI
  const analyzeWithAI = async (customPrompt?: string) => {
    if (!chartData.length) {
      alert('Carica prima i dati del grafico');
      return;
    }

    setAnalyzing(true);
    setAiResponse('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Prepara i dati per l'AI
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
        
        {/* Selettori */}
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
      </div>

      {/* Grafico */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <div ref={chartContainerRef} className="w-full" />
      </div>

      {/* AI Analysis Interface */}
      <div className="flex flex-col gap-4 bg-gray-800 p-6 rounded-lg">
        <h2 className="text-xl font-bold text-white">AI Analysis</h2>
        
        {/* Preset Buttons */}
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

        {/* Custom Prompt */}
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

        {/* AI Response */}
        {aiResponse && (
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">AI Analysis Result</label>
            <div className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg border border-gray-600 whitespace-pre-wrap">
              {aiResponse}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
