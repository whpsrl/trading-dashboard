'use client';

import { useEffect, useState, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-dashboard-production-7a5d.up.railway.app';

interface Pattern {
  pattern: string;
  signal: string;
  strength: number;
}

interface SupportResistance {
  type: string;
  price: number;
  touches: number;
}

interface AIPrediction {
  direction: string;
  confidence: number;
  score?: number;
  ml_score?: number;
  patterns_detected?: string[];
  candlestick_patterns?: Pattern[];
  chart_patterns?: Pattern[];
  support_resistance?: SupportResistance[];
  features?: {
    price_momentum_5: number;
    price_momentum_20: number;
    volatility: number;
    volume_trend: number;
  };
}

export default function Dashboard() {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('H1');
  const [price, setPrice] = useState<number | null>(null);
  const [aiPrediction, setAiPrediction] = useState<AIPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  const timeframes = ['M5', 'M15', 'H1', 'H4', 'D1'];
  const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT'];

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1a1a1a' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#2a2a2a' },
        horzLines: { color: '#2a2a2a' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
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

    chartRef.current = { chart, candlestickSeries };

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const response = await fetch(
          `${API_URL}/api/crypto/${symbol}?timeframe=${timeframe}&limit=200`
        );
        const data = await response.json();

        if (chartRef.current && data.data) {
          chartRef.current.candlestickSeries.setData(data.data);
          setPrice(data.current_price);
          setAiPrediction(data.ai_prediction);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);

    return () => clearInterval(interval);
  }, [symbol, timeframe]);

  const getPredictionColor = (direction: string) => {
    if (direction === 'UP') return 'text-green-400';
    if (direction === 'DOWN') return 'text-red-400';
    return 'text-yellow-400';
  };

  const getPredictionBg = (direction: string) => {
    if (direction === 'UP') return 'bg-green-900/30 border-green-500';
    if (direction === 'DOWN') return 'bg-red-900/30 border-red-500';
    return 'bg-yellow-900/30 border-yellow-500';
  };

  const getPredictionIcon = (direction: string) => {
    if (direction === 'UP') return '↗';
    if (direction === 'DOWN') return '↘';
    return '→';
  };

  const getPatternBadgeColor = (signal: string) => {
    if (signal === 'BULLISH') return 'bg-green-600/20 text-green-400 border-green-500';
    if (signal === 'BEARISH') return 'bg-red-600/20 text-red-400 border-red-500';
    return 'bg-gray-600/20 text-gray-400 border-gray-500';
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">🤖 AI Trading Dashboard</h1>
          <p className="text-gray-400">Real AI with Pattern Recognition & Machine Learning</p>
        </div>

        {/* Controls */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 flex flex-wrap gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Symbol</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-blue-500"
            >
              {symbols.map((sym) => (
                <option key={sym} value={sym}>
                  {sym}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Timeframe</label>
            <div className="flex gap-2">
              {timeframes.map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-4 py-2 rounded font-medium transition-colors ${
                    timeframe === tf
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>

          {price && (
            <div className="ml-auto">
              <label className="block text-sm text-gray-400 mb-2">Current Price</label>
              <div className="text-2xl font-bold text-green-400">
                ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
          )}
        </div>

        {/* AI Prediction Panel - BIG ARROW */}
        {aiPrediction && (
          <div className={`rounded-lg p-6 mb-6 border-2 ${getPredictionBg(aiPrediction.direction)}`}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: Main Prediction with BIG ARROW */}
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <div className={`text-8xl font-bold ${getPredictionColor(aiPrediction.direction)}`}>
                    {getPredictionIcon(aiPrediction.direction)}
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">AI Prediction</div>
                    <div className={`text-4xl font-bold ${getPredictionColor(aiPrediction.direction)}`}>
                      {aiPrediction.direction}
                    </div>
                    <div className="text-lg text-gray-300 mt-1">
                      Confidence: <span className="font-bold">{aiPrediction.confidence}%</span>
                    </div>
                    {aiPrediction.ml_score !== undefined && (
                      <div className="text-sm text-gray-400 mt-1">
                        ML Score: {aiPrediction.ml_score} | Total: {aiPrediction.score}
                      </div>
                    )}
                  </div>
                </div>

                {/* Features */}
                {aiPrediction.features && (
                  <div className="grid grid-cols-2 gap-3 mt-4">
                    <div className="bg-gray-800/50 rounded p-3">
                      <div className="text-xs text-gray-400">Price Momentum (5)</div>
                      <div className={`text-lg font-bold ${aiPrediction.features.price_momentum_5 > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {aiPrediction.features.price_momentum_5 > 0 ? '+' : ''}{aiPrediction.features.price_momentum_5}%
                      </div>
                    </div>
                    <div className="bg-gray-800/50 rounded p-3">
                      <div className="text-xs text-gray-400">Price Momentum (20)</div>
                      <div className={`text-lg font-bold ${aiPrediction.features.price_momentum_20 > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {aiPrediction.features.price_momentum_20 > 0 ? '+' : ''}{aiPrediction.features.price_momentum_20}%
                      </div>
                    </div>
                    <div className="bg-gray-800/50 rounded p-3">
                      <div className="text-xs text-gray-400">Volatility</div>
                      <div className="text-lg font-bold text-purple-400">
                        {aiPrediction.features.volatility}%
                      </div>
                    </div>
                    <div className="bg-gray-800/50 rounded p-3">
                      <div className="text-xs text-gray-400">Volume Trend</div>
                      <div className={`text-lg font-bold ${aiPrediction.features.volume_trend > 0 ? 'text-blue-400' : 'text-gray-400'}`}>
                        {aiPrediction.features.volume_trend > 0 ? '+' : ''}{aiPrediction.features.volume_trend}%
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Right: Patterns Detected */}
              <div>
                <div className="text-sm text-gray-400 mb-3 font-bold">🎯 Patterns Detected</div>
                
                {/* Candlestick Patterns */}
                {aiPrediction.candlestick_patterns && aiPrediction.candlestick_patterns.length > 0 && (
                  <div className="mb-4">
                    <div className="text-xs text-gray-500 mb-2">🕯️ Candlestick:</div>
                    <div className="flex flex-wrap gap-2">
                      {aiPrediction.candlestick_patterns.map((p, idx) => (
                        <div
                          key={idx}
                          className={`px-3 py-1 rounded border text-xs ${getPatternBadgeColor(p.signal)}`}
                        >
                          {p.pattern} (★{p.strength})
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Chart Patterns */}
                {aiPrediction.chart_patterns && aiPrediction.chart_patterns.length > 0 && (
                  <div className="mb-4">
                    <div className="text-xs text-gray-500 mb-2">📊 Chart Patterns:</div>
                    <div className="flex flex-wrap gap-2">
                      {aiPrediction.chart_patterns.map((p, idx) => (
                        <div
                          key={idx}
                          className={`px-3 py-1 rounded border text-xs ${getPatternBadgeColor(p.signal)}`}
                        >
                          {p.pattern} (★{p.strength})
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* All Detected Patterns */}
                {aiPrediction.patterns_detected && aiPrediction.patterns_detected.length > 0 && (
                  <div className="mb-4">
                    <div className="text-xs text-gray-500 mb-2">All Signals:</div>
                    <div className="flex flex-wrap gap-2">
                      {aiPrediction.patterns_detected.map((pattern, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300"
                        >
                          {pattern}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Support/Resistance */}
                {aiPrediction.support_resistance && aiPrediction.support_resistance.length > 0 && (
                  <div>
                    <div className="text-xs text-gray-500 mb-2">Key Levels:</div>
                    <div className="space-y-1">
                      {aiPrediction.support_resistance.slice(0, 3).map((level, idx) => (
                        <div
                          key={idx}
                          className="flex justify-between text-xs bg-gray-800/50 rounded px-2 py-1"
                        >
                          <span className={level.type === 'RESISTANCE' ? 'text-red-400' : 'text-green-400'}>
                            {level.type}
                          </span>
                          <span className="text-gray-300 font-mono">
                            ${level.price.toFixed(2)}
                          </span>
                          <span className="text-gray-500">
                            ({level.touches}x)
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Chart */}
        <div className="bg-gray-800 rounded-lg p-4 relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 rounded-lg z-10">
              <div className="text-xl">Analyzing with AI...</div>
            </div>
          )}
          <div ref={chartContainerRef} />
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Symbol</div>
            <div className="text-xl font-bold">{symbol}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Timeframe</div>
            <div className="text-xl font-bold">{timeframe}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">AI Signal</div>
            {aiPrediction && (
              <div className={`text-xl font-bold ${getPredictionColor(aiPrediction.direction)}`}>
                {aiPrediction.direction} {getPredictionIcon(aiPrediction.direction)}
              </div>
            )}
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Patterns</div>
            {aiPrediction && (
              <div className="text-xl font-bold text-purple-400">
                {aiPrediction.patterns_detected?.length || 0}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
