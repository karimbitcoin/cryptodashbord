import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { usePortfolio } from '../../contexts/PortfolioContext';
import CandlestickChart from '../charts/CandlestickChart';
import MarketIndicators from './MarketIndicators';
import CryptoTable from './CryptoTable';
import NewsFeed from '../news/NewsFeed';
import PortfolioView from '../portfolio/PortfolioView';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [cryptocurrencies, setCryptocurrencies] = useState([]);
  const [marketIndicators, setMarketIndicators] = useState({});
  const [selectedCrypto, setSelectedCrypto] = useState('BTCUSDT');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1d');
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const { currentUser, logout } = useAuth();
  const { portfolios } = usePortfolio();

  // Connect to WebSocket for real-time updates
  useEffect(() => {
    // Load initial data
    fetchCryptocurrencies();
    fetchMarketIndicators();

    // WebSocket setup for crypto prices
    let pricesWs = null;
    let indicatorsWs = null;
    let reconnectTimeout = null;

    const connectPricesWebSocket = () => {
      try {
        // Fall back to polling if WebSocket is not available
        const interval = setInterval(fetchCryptocurrencies, 5000);
        return () => clearInterval(interval);
      } catch (error) {
        console.error('Error setting up crypto prices WebSocket:', error);
        // Fallback to polling
        const interval = setInterval(fetchCryptocurrencies, 5000);
        return () => clearInterval(interval);
      }
    };

    const connectIndicatorsWebSocket = () => {
      try {
        // Fall back to polling if WebSocket is not available
        const interval = setInterval(fetchMarketIndicators, 15000);
        return () => clearInterval(interval);
      } catch (error) {
        console.error('Error setting up market indicators WebSocket:', error);
        // Fallback to polling
        const interval = setInterval(fetchMarketIndicators, 15000);
        return () => clearInterval(interval);
      }
    };

    // Connect to WebSockets
    const cleanupPrices = connectPricesWebSocket();
    const cleanupIndicators = connectIndicatorsWebSocket();

    // Cleanup function
    return () => {
      cleanupPrices();
      cleanupIndicators();
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  // Fetch initial data
  const fetchCryptocurrencies = async () => {
    try {
      const response = await axios.get(`${API}/cryptocurrencies`);
      setCryptocurrencies(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching cryptocurrencies:', error);
    }
  };

  const fetchMarketIndicators = async () => {
    try {
      const response = await axios.get(`${API}/market-indicators`);
      setMarketIndicators(response.data);
    } catch (error) {
      console.error('Error fetching market indicators:', error);
    }
  };

  // Handle crypto selection
  const handleSelectCrypto = (symbol) => {
    setSelectedCrypto(symbol);
  };

  // Handle timeframe selection
  const handleTimeframeChange = (timeframe) => {
    setSelectedTimeframe(timeframe);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Navigation */}
      <header className="bg-slate-800 shadow-lg">
        <div className="container mx-auto py-4 px-6">
          <div className="flex justify-between items-center">
            <div className="text-2xl font-bold text-cyan-400">Crypto Dashboard</div>
            <nav className="hidden md:flex space-x-6">
              <button 
                onClick={() => setActiveTab('dashboard')}
                className={`px-2 py-1 rounded ${activeTab === 'dashboard' ? 'text-cyan-400' : 'text-gray-300 hover:text-cyan-400'}`}
              >
                Dashboard
              </button>
              <button 
                onClick={() => setActiveTab('portfolio')}
                className={`px-2 py-1 rounded ${activeTab === 'portfolio' ? 'text-cyan-400' : 'text-gray-300 hover:text-cyan-400'}`}
              >
                Portfolio
              </button>
              <button 
                onClick={() => setActiveTab('news')}
                className={`px-2 py-1 rounded ${activeTab === 'news' ? 'text-cyan-400' : 'text-gray-300 hover:text-cyan-400'}`}
              >
                News
              </button>
              <button 
                onClick={() => setActiveTab('settings')}
                className={`px-2 py-1 rounded ${activeTab === 'settings' ? 'text-cyan-400' : 'text-gray-300 hover:text-cyan-400'}`}
              >
                Settings
              </button>
            </nav>
            <div className="flex items-center space-x-4">
              <button className="bg-slate-700 p-2 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <div className="relative group">
                <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center cursor-pointer">
                  <span className="font-bold">
                    {currentUser?.username?.slice(0, 2)?.toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="absolute right-0 top-12 mt-2 w-48 bg-slate-800 rounded-md shadow-lg z-20 hidden group-hover:block">
                  <div className="py-1">
                    <div className="px-4 py-2 text-sm text-gray-300 border-b border-gray-700">
                      Signed in as <br />
                      <span className="font-semibold">{currentUser?.email}</span>
                    </div>
                    <button
                      onClick={logout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-slate-700"
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Nav */}
      <div className="md:hidden bg-slate-800 p-2 border-t border-slate-700">
        <div className="flex justify-around">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`flex flex-col items-center p-2 ${activeTab === 'dashboard' ? 'text-cyan-400' : 'text-gray-400'}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-xs mt-1">Dashboard</span>
          </button>
          <button 
            onClick={() => setActiveTab('portfolio')}
            className={`flex flex-col items-center p-2 ${activeTab === 'portfolio' ? 'text-cyan-400' : 'text-gray-400'}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-xs mt-1">Portfolio</span>
          </button>
          <button 
            onClick={() => setActiveTab('news')}
            className={`flex flex-col items-center p-2 ${activeTab === 'news' ? 'text-cyan-400' : 'text-gray-400'}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            <span className="text-xs mt-1">News</span>
          </button>
          <button 
            onClick={() => setActiveTab('settings')}
            className={`flex flex-col items-center p-2 ${activeTab === 'settings' ? 'text-cyan-400' : 'text-gray-400'}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-xs mt-1">Settings</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto py-6 px-4">
        {activeTab === 'dashboard' && (
          <>
            {/* Market Indicators */}
            <div className="mb-6">
              <MarketIndicators indicators={marketIndicators} />
            </div>

            {/* Chart */}
            <div className="bg-slate-800 rounded-lg shadow-lg p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center space-x-4">
                  <h2 className="text-xl font-medium">Chart</h2>
                  <select
                    className="bg-slate-700 text-white px-3 py-1 rounded-md"
                    value={selectedCrypto}
                    onChange={(e) => handleSelectCrypto(e.target.value)}
                  >
                    <option value="BTCUSDT">Bitcoin (BTC)</option>
                    <option value="ETHUSDT">Ethereum (ETH)</option>
                    <option value="BNBUSDT">Binance Coin (BNB)</option>
                    <option value="SOLUSDT">Solana (SOL)</option>
                    <option value="ADAUSDT">Cardano (ADA)</option>
                    <option value="XRPUSDT">Ripple (XRP)</option>
                    <option value="DOGEUSDT">Dogecoin (DOGE)</option>
                  </select>
                </div>
                <div className="flex space-x-2">
                  <button 
                    className={`px-3 py-1 rounded-md ${selectedTimeframe === '1h' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                    onClick={() => handleTimeframeChange('1h')}
                  >
                    1H
                  </button>
                  <button 
                    className={`px-3 py-1 rounded-md ${selectedTimeframe === '4h' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                    onClick={() => handleTimeframeChange('4h')}
                  >
                    4H
                  </button>
                  <button 
                    className={`px-3 py-1 rounded-md ${selectedTimeframe === '1d' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                    onClick={() => handleTimeframeChange('1d')}
                  >
                    1D
                  </button>
                  <button 
                    className={`px-3 py-1 rounded-md ${selectedTimeframe === '1w' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                    onClick={() => handleTimeframeChange('1w')}
                  >
                    1W
                  </button>
                </div>
              </div>
              <CandlestickChart symbol={selectedCrypto} timeframe={selectedTimeframe} height={400} />
            </div>

            {/* Cryptocurrency Table */}
            <CryptoTable 
              cryptocurrencies={cryptocurrencies} 
              isLoading={isLoading} 
              onSelectCrypto={handleSelectCrypto}
            />
          </>
        )}

        {activeTab === 'portfolio' && (
          <PortfolioView />
        )}

        {activeTab === 'news' && (
          <div className="bg-slate-800 rounded-lg shadow-lg p-6">
            <NewsFeed limit={9} />
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-slate-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-medium mb-6">Settings</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium mb-4 text-gray-300">Account Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-400 mb-2">Email</label>
                    <input 
                      type="email" 
                      value={currentUser?.email || ''}
                      readOnly
                      className="w-full bg-slate-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-2">Username</label>
                    <input 
                      type="text" 
                      value={currentUser?.username || ''}
                      readOnly
                      className="w-full bg-slate-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    />
                  </div>
                  <button className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-md">
                    Change Password
                  </button>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-4 text-gray-300">Appearance</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-400 mb-2">Theme</label>
                    <select className="w-full bg-slate-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500">
                      <option value="dark">Dark</option>
                      <option value="light">Light</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-400 mb-2">Default Currency</label>
                    <select className="w-full bg-slate-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500">
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                      <option value="JPY">JPY</option>
                    </select>
                  </div>
                  <div className="flex items-center">
                    <input 
                      type="checkbox" 
                      id="notifications" 
                      className="h-5 w-5 text-cyan-600 focus:ring-cyan-500 border-gray-300 rounded"
                    />
                    <label htmlFor="notifications" className="ml-2 block text-gray-300">
                      Enable Notifications
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-8">
              <h3 className="text-lg font-medium mb-4 text-gray-300">API Keys</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-400 mb-2">Binance API Key</label>
                  <input 
                    type="text" 
                    placeholder="Enter your Binance API key"
                    className="w-full bg-slate-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-2">Binance API Secret</label>
                  <input 
                    type="password" 
                    placeholder="Enter your Binance API secret"
                    className="w-full bg-slate-700 text-white rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <button className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-md">
                  Save API Keys
                </button>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-slate-700">
              <button 
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;