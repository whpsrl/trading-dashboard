'use client';

import { useEffect, useState, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

export default function TradingDashboard() {
  const [price, setPrice] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState('1h');
  const [chartData, setChartData] = useState<any[]>([]);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Fetch current price
  useEffect(() => {
    fetchPrice();
    const interval = setInterval(fetchPrice, 10000); // Every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // Fetch and update chart data
  useEffect(() => {
    fetchChartData();
    const interval = setInterval(fetchChartData, 60000); // Every minute
    return () => clearInterval(interval);
  }, [timeframe]);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0f1419' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#1e2329' },
        horzLines: { color: '#1e2329' },
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

    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });
    
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ 
          width: chartContainerRef.current.clientWidth 
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Update chart when data changes
  useEffect(() => {
    if (chartData.length > 0 && candlestickSeriesRef.current && volumeSeriesRef.current) {
      const candleData = chartData.map(d => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }));

      const volumeData = chartData.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#26a69a80' : '#ef535080',
      }));

      candlestickSeriesRef.current.setData(candleData);
      volumeSeriesRef.current.setData(volumeData);
    }
  }, [chartData]);

  const fetchPrice = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/market/price?symbol=BTC/USDT&exchange=binance`
      );
      const data = await response.json();
      setPrice(data);
      setLoading(false);
      setError(null);
    } catch (err) {
      setError('Failed to fetch price');
      setLoading(false);
    }
  };

  const fetchChartData = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/market/ohlcv?symbol=BTC/USDT&timeframe=${timeframe}&limit=100&exchange=binance`
      );
      const data = await response.json();
      
      // Convert OHLCV array to chart format
      const formatted = data.map((candle: any) => ({
        time: Math.floor(candle[0] / 1000), // Convert ms to seconds
        open: candle[1],
        high: candle[2],
        low: candle[3],
        close: candle[4],
        volume: candle[5],
      }));
      
      setChartData(formatted);
    } catch (err) {
      console.error('Failed to fetch chart data:', err);
    }
  };

  const timeframes = [
    { label: '15m', value: '15m' },
    { label: '1h', value: '1h' },
    { label: '4h', value: '4h' },
    { label: '1d', value: '1d' },
  ];

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#0a0e13',
      color: 'white',
      padding: '1rem'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <header style={{ 
          marginBottom: '2rem', 
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', margin: 0 }}>
              📊 Trading Dashboard
            </h1>
            <p style={{ color: '#888', margin: 0 }}>
              Professional Trading Analytics
            </p>
          </div>
          
          {/* Live Badge */}
          <span style={{ 
            background: '#00ff88', 
            color: '#000',
            padding: '0.5rem 1rem',
            borderRadius: '20px',
            fontWeight: 'bold',
            fontSize: '0.9rem'
          }}>
            ✅ LIVE
          </span>
        </header>

        {/* Price Panel */}
        {price && !loading && (
          <div style={{
            background: '#0f1419',
            border: '1px solid #1e2329',
            borderRadius: '10px',
            padding: '1.5rem',
            marginBottom: '1rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.5rem'
          }}>
            <div>
              <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                BTC/USDT
              </div>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold',
                color: '#00ff88'
              }}>
                ${price.price?.toLocaleString('en-US', { 
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2 
                })}
              </div>
            </div>

            <div>
              <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                24h Change
              </div>
              <div style={{ 
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: price.change_24h > 0 ? '#26a69a' : '#ef5350'
              }}>
                {price.change_24h > 0 ? '+' : ''}
                {price.change_24h?.toFixed(2)}%
              </div>
            </div>

            <div>
              <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                24h Volume
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold' }}>
                ${(price.volume_24h / 1e9).toFixed(2)}B
              </div>
            </div>

            <div>
              <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                Source
              </div>
              <div style={{ 
                fontSize: '1.1rem', 
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {price.source || 'Binance'}
                {price.source === 'coingecko' && (
                  <span style={{
                    marginLeft: '0.5rem',
                    fontSize: '0.7rem',
                    background: '#00ff8820',
                    color: '#00ff88',
                    padding: '0.2rem 0.4rem',
                    borderRadius: '4px'
                  }}>
                    Free
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Timeframe Selector */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          marginBottom: '1rem',
          flexWrap: 'wrap'
        }}>
          {timeframes.map(tf => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              style={{
                background: timeframe === tf.value ? '#00ff88' : '#1e2329',
                color: timeframe === tf.value ? '#000' : '#fff',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '5px',
                cursor: 'pointer',
                fontWeight: timeframe === tf.value ? 'bold' : 'normal',
                transition: 'all 0.2s'
              }}
            >
              {tf.label}
            </button>
          ))}
        </div>

        {/* Chart Container */}
        <div style={{
          background: '#0f1419',
          border: '1px solid #1e2329',
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '2rem'
        }}>
          <div ref={chartContainerRef} />
        </div>

        {/* Quick Stats */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          {[
            { icon: '📈', title: 'Technical Analysis', desc: 'Multi-timeframe charts' },
            { icon: '🎯', title: 'Price Alerts', desc: 'Coming soon' },
            { icon: '🤖', title: 'AI Insights', desc: 'Coming soon' },
            { icon: '📊', title: 'Portfolio', desc: 'Coming soon' }
          ].map((feature, i) => (
            <div key={i} style={{
              background: '#0f1419',
              border: '1px solid #1e2329',
              padding: '1.5rem',
              borderRadius: '10px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                {feature.icon}
              </div>
              <h3 style={{ marginBottom: '0.3rem', fontSize: '1.1rem' }}>
                {feature.title}
              </h3>
              <p style={{ color: '#888', fontSize: '0.9rem', margin: 0 }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>

        {/* Footer */}
        <footer style={{ 
          textAlign: 'center', 
          color: '#555',
          paddingTop: '2rem',
          borderTop: '1px solid #1e2329',
          fontSize: '0.9rem'
        }}>
          <p>🚀 Trading Dashboard v2.0 - Professional Trading Analytics</p>
          <p style={{ marginTop: '0.5rem' }}>
            Powered by Railway + Vercel + CoinGecko
          </p>
        </footer>
      </div>
    </div>
  );
}
