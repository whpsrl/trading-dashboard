'use client';

import { useState, useEffect } from 'react';

interface SystemStatus {
  enabled: boolean;
  status: string;
  message: string;
}

export default function AdminPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);

  // Fetch current system status
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/status`);
      const data = await response.json();
      setStatus(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching system status:', error);
      setLoading(false);
    }
  };

  // Toggle system on/off
  const toggleSystem = async () => {
    setToggling(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/toggle`, {
        method: 'POST',
      });
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error toggling system:', error);
      alert('Failed to toggle system');
    } finally {
      setToggling(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Refresh status every 10 seconds
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">🔐 Admin Control Panel</h1>
          <p className="text-gray-400">Master system control - Enable or disable all automated systems</p>
        </div>

        {/* Status Card */}
        <div className="bg-gray-800 rounded-lg p-8 mb-6 border-2" 
             style={{ borderColor: status?.enabled ? '#10b981' : '#ef4444' }}>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">System Status</h2>
              <p className="text-gray-400">{status?.message}</p>
            </div>
            <div className={`w-24 h-24 rounded-full flex items-center justify-center text-4xl ${
              status?.enabled ? 'bg-green-500' : 'bg-red-500'
            }`}>
              {status?.enabled ? '🟢' : '🔴'}
            </div>
          </div>

          {/* Status Details */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-700 rounded p-4">
              <div className="text-sm text-gray-400 mb-1">Status</div>
              <div className="text-xl font-bold uppercase">
                {status?.status}
              </div>
            </div>
            <div className="bg-gray-700 rounded p-4">
              <div className="text-sm text-gray-400 mb-1">State</div>
              <div className="text-xl font-bold">
                {status?.enabled ? 'ENABLED' : 'DISABLED'}
              </div>
            </div>
          </div>

          {/* Toggle Button */}
          <button
            onClick={toggleSystem}
            disabled={toggling}
            className={`w-full py-4 rounded-lg font-bold text-xl transition-all ${
              status?.enabled
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-green-600 hover:bg-green-700'
            } ${toggling ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {toggling ? (
              'TOGGLING...'
            ) : status?.enabled ? (
              '🔴 DISABLE SYSTEM'
            ) : (
              '🟢 ENABLE SYSTEM'
            )}
          </button>
        </div>

        {/* Systems Info */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">📊 Controlled Systems</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between bg-gray-700 rounded p-3">
              <span>📊 Crypto Auto-Scan (4H)</span>
              <span className={status?.enabled ? 'text-green-400' : 'text-red-400'}>
                {status?.enabled ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <div className="flex items-center justify-between bg-gray-700 rounded p-3">
              <span>🥇 Commodities Auto-Scan (4H)</span>
              <span className={status?.enabled ? 'text-green-400' : 'text-red-400'}>
                {status?.enabled ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <div className="flex items-center justify-between bg-gray-700 rounded p-3">
              <span>📈 Indices Auto-Scan (4H)</span>
              <span className={status?.enabled ? 'text-green-400' : 'text-red-400'}>
                {status?.enabled ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <div className="flex items-center justify-between bg-gray-700 rounded p-3">
              <span>📰 News Articles Generator</span>
              <span className={status?.enabled ? 'text-green-400' : 'text-red-400'}>
                {status?.enabled ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <div className="flex items-center justify-between bg-gray-700 rounded p-3">
              <span>🔄 Trade Tracker (TP/SL Monitor)</span>
              <span className={status?.enabled ? 'text-green-400' : 'text-red-400'}>
                {status?.enabled ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
          </div>
        </div>

        {/* Warning */}
        <div className="mt-6 bg-yellow-900 border-2 border-yellow-600 rounded-lg p-4">
          <div className="flex items-start">
            <span className="text-2xl mr-3">⚠️</span>
            <div>
              <h4 className="font-bold mb-1">Warning</h4>
              <p className="text-sm text-gray-300">
                Disabling the system will stop all automated scans, trade tracking, and news generation.
                Manual scans will still work. The system state persists across restarts.
              </p>
            </div>
          </div>
        </div>

        {/* Back Link */}
        <div className="mt-6 text-center">
          <a href="/" className="text-blue-400 hover:text-blue-300">
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}

