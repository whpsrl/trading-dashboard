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
];

const TIMEFRAMES = [
  { value: 'M5', label: '5 Minutes' },
  { value: 'M15', label: '15 Minutes' },
  { value: 'H1', label: '1 Hour' },
  { value: 'H4', label: '4 Hours' },
  { value: 'D1', label: '1 Day' },
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
  const [drawnLines, setDrawnLines] = useState<any[]>([]);
  const [autoDrawing, setAutoDrawing] = useState(false);
  
  // Dynamic symbol list
  const [availableSymbols, setAvailableSymbols] = useState(SYMBOLS);
  const [symbolSearch, setSymbolSearch] = useState('');
  const [filteredSymbols, setFilteredSymbols] = useState(SYMBOLS);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const drawnLinesRef = useRef<any[]>([]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
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

  // Load chart data when symbol or timeframe changes
  useEffect(() => {
    loadChartData();
  }, [selectedSymbol, selectedTimeframe]);

  // Filter symbols based on search
  useEffect(() => {
    if (symbolSearch.trim() === '') {
      setFilteredSymbols(availableSymbols);
    } else {
      const search = symbolSearch.toLowerCase();
      const filtered = availableSymbols.filter(s => 
        s.value.toLowerCase().includes(search) || 
        s.label.toLowerCase().includes(search)
      );
      setFilteredSymbols(filtered);
      
      // If current selected symbol is not in filtered list, select first filtered
      if (filtered.length > 0 && !filtered.find(s => s.value === selectedSymbol.value)) {
        setSelectedSymbol(filtered[0]);
      }
    }
  }, [symbolSearch, availableSymbols]);

  // Load all available symbols from Binance on mount
  useEffect(() => {
    const loadAllSymbols = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/instruments/binance`);
        const data = await response.json();
        
        if (data.success && data.instruments) {
          const symbols = data.instruments.map((inst: any) => ({
            value: inst.symbol,
            label: inst.name,
            type: 'crypto'
          }));
          setAvailableSymbols(symbols);
          setFilteredSymbols(symbols);
        }
      } catch (error) {
        console.error('Failed to load symbols:', error);
        // Keep default hardcoded list if API fails
      }
    };
    
    loadAllSymbols();
  }, []);

  const loadChartData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const endpoint = `${apiUrl}/api/crypto/${selectedSymbol.value}?timeframe=${selectedTimeframe.value}&limit=1000`;
      
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

  // NEW: Best Trade - AI decides LONG or SHORT automatically
  const analyzeBestTrade = async () => {
    if (!chartData.length) return;

    setAnalyzing(true);
    setAiResponse('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const marketContext = {
        symbol: selectedSymbol.label,
        timeframe: selectedTimeframe.label,
        currentPrice: chartData[chartData.length - 1]?.close,
        recentCandles: chartData.slice(-150).map(d => ({
          time: new Date(d.time * 1000).toISOString(),
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          volume: d.volume,
        })),
      };

      const bestTradePrompt = `Tu sei un trader professionista. Analizza ${selectedSymbol.label} su timeframe ${selectedTimeframe.label} e trova IL MIGLIOR TRADE possibile (LONG o SHORT).

Dati di mercato:
${JSON.stringify(marketContext, null, 2)}

IMPORTANTE: Devi SEMPRE fornire un trade setup (anche se il mercato è laterale, trova il setup migliore).

Fornisci la risposta in questo formato ESATTO:

## 🎯 BEST TRADE SETUP

### Direction
**[LONG o SHORT]** (scegli quello con più probabilità di successo)

### Signal Strength
- **Overall Score**: X/10
- **Confidence**: XX%
- **Setup Quality**: Strong/Medium/Weak

### Entry Strategy
- **Entry Price**: $XX.XX
- **Stop Loss**: $XX.XX
- **Take Profit 1**: $XX.XX
- **Take Profit 2**: $XX.XX (optional)
- **Risk/Reward**: X.X:1

### Why This Direction?
- [Motivo principale 1]
- [Motivo principale 2]
- [Motivo principale 3]
- [Conferma pattern/indicatori]

### Market Context
- **Trend**: Bullish/Bearish/Neutral
- **Volume**: Strong/Weak
- **Momentum**: Increasing/Decreasing
- **Key Level**: $XX.XX

### Action Plan
**[ENTER NOW / WAIT FOR PULLBACK / WAIT FOR BREAKOUT]**

Se "WAIT", specifica: "Wait for price to reach $XX.XX then enter"

### Risk Warning
[Eventuale rischio o scenario alternativo]

---
**Bottom Line**: [Una frase conclusiva chiara tipo "Strong LONG setup with 7.5/10 score - Enter now" oppure "Weak setup, wait for better entry"]`;

      const response = await fetch(`${apiUrl}/api/v1/ai/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: bestTradePrompt }),
      });

      const result = await response.json();
      setAiResponse(result.analysis || 'Nessuna risposta');
    } catch (error) {
      setAiResponse('Errore durante l\'analisi del best trade');
    } finally {
      setAnalyzing(false);
    }
  };

  // NEW: Analyze BUY or SELL signal
  const analyzeSignal = async (signal: 'buy' | 'sell') => {
    if (!chartData.length) return;

    setAnalyzing(true);
    setAiResponse('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const marketContext = {
        symbol: selectedSymbol.label,
        timeframe: selectedTimeframe.label,
        currentPrice: chartData[chartData.length - 1]?.close,
        recentCandles: chartData.slice(-100).map(d => ({
          time: new Date(d.time * 1000).toISOString(),
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          volume: d.volume,
        })),
      };

      const signalPrompt = signal === 'buy' 
        ? `Analizza ${selectedSymbol.label} su timeframe ${selectedTimeframe.label} per SEGNALE DI ACQUISTO (LONG).

Dati: ${JSON.stringify(marketContext, null, 2)}

Fornisci:
## 📈 BUY SIGNAL

### Signal Strength
- **Strength**: X/10
- **Confidence**: XX%
- **Entry**: $XX
- **Stop Loss**: $XX
- **Take Profit**: $XX

### Reasons
- Pattern candlestick
- Trend
- Volume
- S/R levels

### Risk/Reward
- R/R ratio: X:1
- Risk level: Low/Medium/High

**Action**: BUY NOW / WAIT / NO SIGNAL`
        : `Analizza ${selectedSymbol.label} su timeframe ${selectedTimeframe.label} per SEGNALE DI VENDITA (SHORT).

Dati: ${JSON.stringify(marketContext, null, 2)}

Fornisci:
## 📉 SELL SIGNAL

### Signal Strength
- **Strength**: X/10
- **Confidence**: XX%
- **Entry**: $XX
- **Stop Loss**: $XX
- **Take Profit**: $XX

### Reasons
- Pattern candlestick
- Trend
- Volume
- S/R levels

### Risk/Reward
- R/R ratio: X:1
- Risk level: Low/Medium/High

**Action**: SELL NOW / WAIT / NO SIGNAL`;

      const response = await fetch(`${apiUrl}/api/v1/ai/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: signalPrompt }),
      });

      const result = await response.json();
      setAiResponse(result.analysis || 'Nessuna risposta');
    } catch (error) {
      setAiResponse('Errore segnale');
    } finally {
      setAnalyzing(false);
    }
  };

  // NEW: Currency Strength
  const analyzeCurrencyStrength = async () => {
    if (!chartData.length) return;

    setAnalyzing(true);
    setAiResponse('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const marketContext = {
        symbol: selectedSymbol.label,
        timeframe: selectedTimeframe.label,
        currentPrice: chartData[chartData.length - 1]?.close,
        recentCandles: chartData.slice(-200).map(d => ({
          time: new Date(d.time * 1000).toISOString(),
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          volume: d.volume,
        })),
      };

      const strengthPrompt = `Analizza FORZA di ${selectedSymbol.label} su ${selectedTimeframe.label}.

Dati: ${JSON.stringify(marketContext, null, 2)}

Fornisci:
## 💪 CURRENCY STRENGTH

### Strength Score
- **Overall**: X/10
- **Momentum**: Strong/Medium/Weak
- **Volume**: Strong/Medium/Weak
- **Volatility**: High/Medium/Low

### Performance
- vs recent highs/lows
- Trend consistency
- Breakout potential

### Multi-Timeframe
- Current TF: ${selectedTimeframe.label}
- Higher TF view
- Alignment?

**Conclusion**: STRONG/NEUTRAL/WEAK`;

      const response = await fetch(`${apiUrl}/api/v1/ai/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: strengthPrompt }),
      });

      const result = await response.json();
      setAiResponse(result.analysis || 'Nessuna risposta');
    } catch (error) {
      setAiResponse('Errore strength');
    } finally {
      setAnalyzing(false);
    }
  };

  // NEW: Breakout Levels
  const analyzeBreakoutLevels = async () => {
    if (!chartData.length) return;

    setAnalyzing(true);
    setAiResponse('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const marketContext = {
        symbol: selectedSymbol.label,
        timeframe: selectedTimeframe.label,
        currentPrice: chartData[chartData.length - 1]?.close,
        priceHigh: Math.max(...chartData.map(d => d.high)),
        priceLow: Math.min(...chartData.map(d => d.low)),
        recentCandles: chartData.slice(-150).map(d => ({
          time: new Date(d.time * 1000).toISOString(),
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          volume: d.volume,
        })),
      };

      const breakoutPrompt = `Identifica LIVELLI DI ROTTURA per ${selectedSymbol.label} su ${selectedTimeframe.label}.

Dati: ${JSON.stringify(marketContext, null, 2)}

Fornisci:
## ⚡ BREAKOUT LEVELS

### Key Levels
1. **Level**: $XX
   - Type: Resistance/Support
   - Strength: Strong/Medium/Weak
   - If breaks: → Target $XX

2. **Level**: $XX
   - Type: Resistance/Support
   - Strength: Strong/Medium/Weak
   - If breaks: → Target $XX

3. **Level**: $XX
   - Type: Resistance/Support
   - Strength: Strong/Medium/Weak
   - If breaks: → Target $XX

### Current Position
- Price vs levels
- Nearest breakout
- Probability of break

**Watch**: Quale livello monitorare`;

      const response = await fetch(`${apiUrl}/api/v1/ai/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: breakoutPrompt }),
      });

      const result = await response.json();
      setAiResponse(result.analysis || 'Nessuna risposta');
    } catch (error) {
      setAiResponse('Errore breakout');
    } finally {
      setAnalyzing(false);
    }
  };

  const clearAllLines = () => {
    // Remove all drawn lines from chart
    if (chartRef.current) {
      drawnLinesRef.current.forEach(lineSeries => {
        try {
          chartRef.current?.removeSeries(lineSeries);
        } catch (e) {
          console.error('Error removing line:', e);
        }
      });
    }
    drawnLinesRef.current = [];
    setDrawnLines([]);
  };

  const autoDrawLines = async (drawType: string) => {
    if (!chartData.length || !chartRef.current) return;

    setAutoDrawing(true);

    try{
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const candles = chartData.map(d => ({
        time: new Date(d.time * 1000).toISOString(),
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
        volume: d.volume
      }));

      const response = await fetch(`${apiUrl}/api/v1/ai/auto-draw`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: selectedSymbol.label,
          timeframe: selectedTimeframe.label,
          candles: candles,
          drawType: drawType
        }),
      });

      const result = await response.json();
      
      if (result.success && result.lines) {
        const chart = chartRef.current;
        const newLines: any[] = [];

        result.lines.forEach((line: any) => {
          if (line.type === 'support' || line.type === 'resistance') {
            const lineSeries = chart.addLineSeries({
              color: line.color || (line.type === 'support' ? '#22c55e' : '#ef4444'),
              lineWidth: 2,
              priceLineVisible: false,
              lastValueVisible: false,
            });
            
            const lineData = chartData.map(candle => ({
              time: candle.time,
              value: line.price
            }));
            
            lineSeries.setData(lineData);
            newLines.push(lineSeries);
          }
          
          if (line.type === 'trendline' && line.points && line.points.length >= 2) {
            const lineSeries = chart.addLineSeries({
              color: line.color || '#3b82f6',
              lineWidth: 2,
              priceLineVisible: false,
              lastValueVisible: false,
            });
            
            const lineData = line.points.map((point: any) => ({
              time: (new Date(point.time).getTime() / 1000) as UTCTimestamp,
              value: point.price
            }));
            
            lineSeries.setData(lineData);
            newLines.push(lineSeries);
          }
        });

        drawnLinesRef.current = [...drawnLinesRef.current, ...newLines];
        setDrawnLines([...drawnLines, ...result.lines]);
      }
    } catch (error) {
      console.error('Auto-draw error:', error);
    } finally {
      setAutoDrawing(false);
    }
  };

  useEffect(() => {
    loadChartData();
  }, [selectedSymbol, selectedTimeframe]);

  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: '65% 35%',
      height: '100vh',
      width: '100vw',
      background: 'linear-gradient(to bottom right, #0f172a, #1e3a8a, #0f172a)',
      overflow: 'hidden'
    }}>
      
      {/* LEFT COLUMN: Chart */}
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        
        {/* Controls */}
        <div style={{ 
          display: 'flex', 
          gap: '1rem', 
          alignItems: 'center',
          padding: '1rem',
          backgroundColor: 'rgba(30, 41, 59, 0.8)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(59, 130, 246, 0.3)'
        }}>
          <h1 style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold',
            background: 'linear-gradient(to right, #60a5fa, #22d3ee)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>Chart Analyzer</h1>
          
          <input
            type="text"
            placeholder="🔍 Search symbol..."
            value={symbolSearch}
            onChange={(e) => setSymbolSearch(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#1e293b',
              color: 'white',
              borderRadius: '0.5rem',
              border: '1px solid #475569',
              fontSize: '0.875rem',
              width: '150px'
            }}
          />
          
          <select
            value={selectedSymbol.value}
            onChange={(e) => {
              const found = availableSymbols.find(s => s.value === e.target.value);
              if (found) {
                setSelectedSymbol(found);
                setSymbolSearch(''); // Clear search after selection
              }
            }}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#334155',
              color: 'white',
              borderRadius: '0.5rem',
              border: '1px solid #2563eb',
              maxWidth: '200px'
            }}
          >
            {filteredSymbols.map((sym) => (
              <option key={sym.value} value={sym.value}>{sym.label}</option>
            ))}
          </select>

          <select
            value={selectedTimeframe.value}
            onChange={(e) => setSelectedTimeframe(TIMEFRAMES.find(t => t.value === e.target.value)!)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#334155',
              color: 'white',
              borderRadius: '0.5rem',
              border: '1px solid #2563eb'
            }}
          >
            {TIMEFRAMES.map((tf) => (
              <option key={tf.value} value={tf.value}>{tf.label}</option>
            ))}
          </select>

          <button
            onClick={loadChartData}
            disabled={loading}
            style={{
              padding: '0.5rem 1.5rem',
              backgroundColor: '#2563eb',
              color: 'white',
              borderRadius: '0.5rem',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          
          {chartData.length > 0 && (
            <span style={{ color: '#4ade80', fontSize: '0.875rem', marginLeft: 'auto' }}>
              ✓ {chartData.length} candles
            </span>
          )}
        </div>

        {/* Chart */}
        <div style={{ flex: 1, padding: '1rem', backgroundColor: '#0f172a' }}>
          <div 
            ref={chartContainerRef} 
            style={{ 
              width: '100%', 
              height: '100%',
              borderRadius: '0.5rem',
              border: '1px solid rgba(59, 130, 246, 0.3)'
            }} 
          />
        </div>
      </div>

      {/* RIGHT COLUMN: AI Panel */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'rgba(15, 23, 42, 0.8)',
        backdropFilter: 'blur(12px)',
        borderLeft: '1px solid rgba(59, 130, 246, 0.3)',
        overflow: 'hidden'
      }}>
        
        {/* AI Controls */}
        <div style={{ 
          padding: '1rem',
          borderBottom: '1px solid rgba(59, 130, 246, 0.3)',
          flexShrink: 0
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#60a5fa', marginBottom: '1rem' }}>
            🤖 AI Trading Signals
          </h2>
          
          {/* Trading Signal Buttons */}
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <button
                onClick={() => analyzeBestTrade()}
                disabled={analyzing || !chartData.length}
                style={{
                  width: '100%',
                  padding: '1rem',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  borderRadius: '0.75rem',
                  fontSize: '1rem',
                  fontWeight: '700',
                  textAlign: 'center',
                  cursor: (analyzing || !chartData.length) ? 'not-allowed' : 'pointer',
                  opacity: (analyzing || !chartData.length) ? 0.5 : 1,
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.75rem',
                  boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                  transition: 'all 0.3s ease'
                }}
              >
                <span style={{ fontSize: '2rem' }}>🎯</span>
                <span>{analyzing ? 'Analyzing...' : 'Find Best Trade'}</span>
              </button>
            </div>
          </div>

          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem', marginTop: '1rem', fontWeight: '600' }}>
            ADVANCED ANALYSIS
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginBottom: '1rem' }}>
            <button
              onClick={() => analyzeCurrencyStrength()}
              disabled={analyzing || !chartData.length}
              style={{
                width: '100%',
                padding: '0.5rem',
                background: 'rgba(139, 92, 246, 0.2)',
                color: '#a78bfa',
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: (analyzing || !chartData.length) ? 'not-allowed' : 'pointer',
                opacity: (analyzing || !chartData.length) ? 0.5 : 1,
                border: '1px solid rgba(139, 92, 246, 0.3)',
              }}
            >
              💪 Strength Analysis
            </button>

            <button
              onClick={() => analyzeBreakoutLevels()}
              disabled={analyzing || !chartData.length}
              style={{
                width: '100%',
                padding: '0.5rem',
                background: 'rgba(245, 158, 11, 0.2)',
                color: '#fbbf24',
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: (analyzing || !chartData.length) ? 'not-allowed' : 'pointer',
                opacity: (analyzing || !chartData.length) ? 0.5 : 1,
                border: '1px solid rgba(245, 158, 11, 0.3)',
              }}
            >
              ⚡ Breakout Levels
            </button>
          </div>

          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem', marginTop: '1rem', fontWeight: '600' }}>
            CUSTOM ANALYSIS
          </div>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Custom analysis..."
            style={{
              width: '100%',
              padding: '0.5rem',
              backgroundColor: '#1e293b',
              color: 'white',
              borderRadius: '0.375rem',
              border: '1px solid #1d4ed8',
              fontSize: '0.75rem',
              resize: 'none',
              marginBottom: '0.375rem'
            }}
            rows={2}
          />
          <button
            onClick={() => analyzeWithAI()}
            disabled={analyzing || !prompt.trim() || !chartData.length}
            style={{
              width: '100%',
              padding: '0.375rem',
              backgroundColor: '#059669',
              color: 'white',
              borderRadius: '0.375rem',
              fontWeight: '600',
              fontSize: '0.75rem',
              cursor: (analyzing || !prompt.trim() || !chartData.length) ? 'not-allowed' : 'pointer',
              opacity: (analyzing || !prompt.trim() || !chartData.length) ? 0.5 : 1,
              border: 'none'
            }}
          >
            {analyzing ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {/* AI Results */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto',
          padding: '1rem',
          backgroundColor: 'rgba(2, 6, 23, 0.7)'
        }}>
          {analyzing && (
            <div style={{ textAlign: 'center', paddingTop: '3rem' }}>
              <div style={{ 
                width: '3rem', 
                height: '3rem', 
                border: '4px solid #2563eb',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 1rem'
              }} />
              <div style={{ color: '#60a5fa' }}>Analyzing...</div>
            </div>
          )}

          {!aiResponse && !analyzing && (
            <div style={{ textAlign: 'center', paddingTop: '3rem', color: '#6b7280' }}>
              <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🤖</div>
              <div>Select an analysis</div>
            </div>
          )}

          {aiResponse && (
            <div style={{ color: '#d1d5db', fontSize: '0.875rem', lineHeight: '1.6' }}>
              {aiResponse.split('\n\n').map((block, idx) => {
                if (block.startsWith('##')) {
                  return (
                    <div key={idx} style={{ 
                      backgroundColor: 'rgba(37, 99, 235, 0.2)',
                      border: '1px solid rgba(37, 99, 235, 0.3)',
                      borderRadius: '0.5rem',
                      padding: '1rem',
                      marginBottom: '1rem'
                    }}>
                      <h3 style={{ color: '#60a5fa', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                        {block.replace(/^##\s*/, '')}
                      </h3>
                    </div>
                  );
                }
                return (
                  <div key={idx} style={{ marginBottom: '0.75rem' }}>
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
