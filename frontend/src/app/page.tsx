'use client';

import { useEffect, useState, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import AIAnalysisPanel from '@/components/AIAnalysisPanel';

export default function TradingDashboard() {
  const [selectedAsset, setSelectedAsset] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [price, setPrice] = useState<any>(null);
  const [timeframe, setTimeframe] = useState('1h');
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Popular assets for quick access
  const popularAssets = [
    { symbol: 'BTC/USDT', name: 'Bitcoin', type: 'crypto', icon: '₿' },
    { symbol: 'ETH/USDT', name: 'Ethereum', type: 'crypto', icon: 'Ξ' },
    { symbol: 'AAPL', name: 'Apple', type: 'stock', icon: '🍎' },
    { symbol: 'TSLA', name: 'Tesla', type: 'stock', icon: '🚗' },
    { symbol: '^GSPC', name: 'S&P 500', type: 'index', icon: '📈' },
    { symbol: 'GC=F', name: 'Gold', type: 'commodity', icon: '🥇' },
  ];

  // Initialize with Bitcoin
  useEffect(() => {
    if (!selectedAsset) {
      setSelectedAsset(popularAssets[0]);
    }
  }, []);

  // Fetch price
  useEffect(() => {
    if (selectedAsset) {
      fetchPrice();
      const interval = setInterval(fetchPrice, 15000);
      return () => clearInterval(interval);
    }
  }, [selectedAsset]);

  // Fetch chart
  useEffect(() => {
    if (selectedAsset) {
      fetchChartData();
      const interval = setInterval(fetchChartData, 60000);
      return () => clearInterval(interval);
    }
  }, [timeframe, selectedAsset]);

  // Search assets
  useEffect(() => {
    if (searchQuery.length >= 2) {
      searchAssets();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

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
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
    
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Update chart
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
    if (!selectedAsset) return;
    try {
      const response = await fetch(
        `${API_URL}/api/market/price?symbol=${selectedAsset.symbol}&asset_type=${selectedAsset.type}&exchange=binance`
      );
      const data = await response.json();
      setPrice(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch price:', err);
      setLoading(false);
    }
  };

  const fetchChartData = async () => {
    if (!selectedAsset) return;
    try {
      const response = await fetch(
        `${API_URL}/api/market/ohlcv?symbol=${selectedAsset.symbol}&timeframe=${timeframe}&limit=100&asset_type=${selectedAsset.type}&exchange=binance`
      );
      const data = await response.json();
      
      const formatted = data.map((candle: any) => ({
        time: Math.floor(candle[0] / 1000),
        open: candle[1],
        high: candle[2],
        low: candle[3],
        close: candle[4],
        volume: candle[5],
      }));
      
      setChartData(formatted);
    } catch (err) {
      console.error('Failed to fetch chart:', err);
    }
  };

  const searchAssets = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/market/search?query=${searchQuery}`
      );
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
    }
  };

  const selectAsset = (asset: any) => {
    setSelectedAsset(asset);
    setSearchQuery('');
    setSearchResults([]);
  };

  const toggleWatchlist = (symbol: string) => {
    if (watchlist.includes(symbol)) {
      setWatchlist(watchlist.filter(s => s !== symbol));
    } else {
      setWatchlist([...watchlist, symbol]);
    }
  };

  const timeframes = [
    { label: '15m', value: '15m' },
    { label: '1h', value: '1h' },
    { label: '4h', value: '4h' },
    { label: '1d', value: '1d' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#0a0e13', color: 'white', padding: '1rem' }}>
      <div style={{ maxWidth: '1600px', margin: '0 auto' }}>
        
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
              🌍 Global Markets Pro
            </h1>
            <p style={{ color: '#888', margin: 0 }}>
              Real-time • 15min Intraday • AI-Powered Analysis
            </p>
          </div>
          <span style={{ 
            background: '#00ff88', 
            color: '#000', 
            padding: '0.5rem 1rem', 
            borderRadius: '20px', 
            fontWeight: 'bold' 
          }}>
            ✅ LIVE
          </span>
        </header>

        {/* Search Bar */}
        <div style={{ marginBottom: '1.5rem', position: 'relative' }}>
          <input
            type="text"
            placeholder="🔍 Search crypto, stocks, forex, indices, commodities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '1rem',
              background: '#0f1419',
              border: '1px solid #1e2329',
              borderRadius: '10px',
              color: 'white',
              fontSize: '1rem',
            }}
          />
          
          {/* Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: '#0f1419',
              border: '1px solid #1e2329',
              borderRadius: '10px',
              marginTop: '0.5rem',
              maxHeight: '400px',
              overflowY: 'auto',
              zIndex: 1000,
            }}>
              {searchResults.map((asset, idx) => (
                <div
                  key={idx}
                  onClick={() => selectAsset(asset)}
                  style={{
                    padding: '1rem',
                    borderBottom: '1px solid #1e2329',
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#1a1f25'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{asset.symbol}</div>
                      <div style={{ fontSize: '0.9rem', color: '#888' }}>{asset.name}</div>
                    </div>
                    <div style={{
                      padding: '0.3rem 0.6rem',
                      background: '#1e2329',
                      borderRadius: '5px',
                      fontSize: '0.8rem',
                      textTransform: 'capitalize',
                    }}>
                      {asset.type}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Popular Assets */}
        <div style={{
          background: '#0f1419',
          border: '1px solid #1e2329',
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '1rem',
        }}>
          <div style={{ marginBottom: '0.75rem', color: '#888', fontSize: '0.9rem' }}>
            ⭐ Popular
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {popularAssets.map(asset => (
              <button
                key={asset.symbol}
                onClick={() => selectAsset(asset)}
                style={{
                  background: selectedAsset?.symbol === asset.symbol ? '#00ff88' : '#1e2329',
                  color: selectedAsset?.symbol === asset.symbol ? '#000' : '#fff',
                  border: 'none',
                  padding: '0.75rem 1.25rem',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: selectedAsset?.symbol === asset.symbol ? 'bold' : 'normal',
                  transition: 'all 0.2s',
                }}>
                {asset.icon} {asset.name}
              </button>
            ))}
          </div>
        </div>

        {/* Current Asset Info */}
        {selectedAsset && price && !loading && (
          <div style={{
            background: '#0f1419',
            border: '1px solid #1e2329',
            borderRadius: '10px',
            padding: '1.5rem',
            marginBottom: '1rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.5rem',
          }}>
            <div>
              <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                {selectedAsset.name}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00ff88' }}>
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
                Type
              </div>
              <div style={{
                fontSize: '1.1rem',
                fontWeight: 'bold',
                textTransform: 'capitalize',
              }}>
                {selectedAsset.type}
              </div>
            </div>

            <div>
              <button
                onClick={() => toggleWatchlist(selectedAsset.symbol)}
                style={{
                  background: watchlist.includes(selectedAsset.symbol) ? '#f7931a' : '#1e2329',
                  color: '#fff',
                  border: 'none',
                  padding: '0.75rem 1.25rem',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                }}
              >
                {watchlist.includes(selectedAsset.symbol) ? '⭐ In Watchlist' : '☆ Add to Watchlist'}
              </button>
            </div>
          </div>
        )}

        {/* Timeframes */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
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
              }}
            >
              {tf.label}
            </button>
          ))}
        </div>

        {/* Chart */}
        <div style={{
          background: '#0f1419',
          border: '1px solid #1e2329',
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '2rem',
        }}>
          {loading && (
            <div style={{ 
              height: '500px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              color: '#888'
            }}>
              Loading chart...
            </div>
          )}
          <div ref={chartContainerRef} style={{ display: loading ? 'none' : 'block' }} />
        </div>

        {/* AI Analysis Panel */}
        {selectedAsset && (
          <AIAnalysisPanel 
            symbol={selectedAsset.symbol}
            assetType={selectedAsset.type}
            apiUrl={API_URL}
          />
        )}

        {/* Footer */}
        <footer style={{ 
          textAlign: 'center', 
          color: '#555',
          paddingTop: '2rem',
          borderTop: '1px solid #1e2329',
          fontSize: '0.9rem',
          marginTop: '2rem'
        }}>
          <p>🌍 Global Markets Pro - Real-time Data • AI Analysis</p>
          <p style={{ marginTop: '0.5rem' }}>
            Powered by Railway + Vercel + Binance + Finnhub + Claude AI
          </p>
        </footer>
      </div>
    </div>
  );
}
