'use client';

import { useEffect, useState, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-dashboard-production-7a5d.up.railway.app';

export default function Dashboard() {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('H1');
  const [price, setPrice] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

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

        if (chartRef.current) {
          chartRef.current.candlestickSeries.setData(data.data);
          setPrice(data.current_price);
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

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Trading Dashboard</h1>
          <p className="text-gray-400">Real-time market analysis</p>
        </div>

        {/* Controls */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 flex flex-wrap gap-4">
          {/* Symbol Selector */}
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

          {/* Timeframe Selector */}
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

          {/* Price Display */}
          {price && (
            <div className="ml-auto">
              <label className="block text-sm text-gray-400 mb-2">Current Price</label>
              <div className="text-2xl font-bold text-green-400">
                ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
          )}
        </div>

        {/* Chart */}
        <div className="bg-gray-800 rounded-lg p-4">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 rounded-lg">
              <div className="text-xl">Loading...</div>
            </div>
          )}
          <div ref={chartContainerRef} />
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Active Symbol</div>
            <div className="text-xl font-bold">{symbol}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Timeframe</div>
            <div className="text-xl font-bold">{timeframe}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Status</div>
            <div className="text-xl font-bold text-green-400">Live</div>
          </div>
        </div>
      </div>
    </div>
  );
}
