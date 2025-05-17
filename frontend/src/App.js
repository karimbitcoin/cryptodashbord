import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import { createChart, CrosshairMode } from 'lightweight-charts';
import { io } from 'socket.io-client';
import moment from 'moment';
import { FaBitcoin, FaEthereum } from 'react-icons/fa';
import { SiCardano, SiLitecoin, SiDogecoin, SiBinance, SiSolana } from 'react-icons/si';

// Auth and Portfolio
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { PortfolioProvider } from './contexts/PortfolioContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import PortfolioView from './components/portfolio/PortfolioView';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { currentUser, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }
  
  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Function to format large numbers with commas and abbreviations
const formatNumber = (number, decimals = 2) => {
  if (number === undefined || number === null) return '0';
  
  if (number >= 1000000000) {
    return `$${(number / 1000000000).toFixed(decimals)}B`;
  } else if (number >= 1000000) {
    return `$${(number / 1000000).toFixed(decimals)}M`;
  } else if (number >= 1000) {
    return `$${(number / 1000).toFixed(decimals)}K`;
  } else {
    return `$${number.toFixed(decimals)}`;
  }
};

// Function to get crypto icon
const getCryptoIcon = (symbol) => {
  const iconStyle = { fontSize: '1.4rem' };
  
  if (symbol.includes('BTC')) return <FaBitcoin style={iconStyle} className="text-yellow-500" />;
  if (symbol.includes('ETH')) return <FaEthereum style={iconStyle} className="text-blue-400" />;
  if (symbol.includes('BNB')) return <SiBinance style={iconStyle} className="text-yellow-400" />;
  if (symbol.includes('ADA')) return <SiCardano style={iconStyle} className="text-blue-500" />;
  if (symbol.includes('SOL')) return <SiSolana style={iconStyle} className="text-purple-500" />;
  if (symbol.includes('LTC')) return <SiLitecoin style={iconStyle} className="text-gray-400" />;
  if (symbol.includes('DOGE')) return <SiDogecoin style={iconStyle} className="text-yellow-400" />;
  
  // Default icon for other coins
  return <div style={iconStyle} className="bg-blue-500 rounded-full w-6 h-6 flex items-center justify-center text-white font-bold">
    {symbol.slice(0, 1)}
  </div>;
};

// Dashboard Component
const Dashboard = () => {
  const [cryptocurrencies, setCryptocurrencies] = useState([]);
  const [marketIndicators, setMarketIndicators] = useState({
    total_market_cap: 0,
    total_volume_24h: 0,
    btc_dominance: 0,
    eth_dominance: 0,
    fear_greed_index: 50
  });
  const [selectedCrypto, setSelectedCrypto] = useState('BTCUSDT');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);

  // Connect to WebSocket for real-time updates
  useEffect(() => {
    // Load initial data
    fetchCryptocurrencies();
    fetchMarketIndicators();
    fetchChartData(selectedCrypto, selectedTimeframe);

    // WebSocket setup for crypto prices
    let pricesWs = null;
    let indicatorsWs = null;
    let reconnectTimeout = null;

    const connectPricesWebSocket = () => {
      const pricesWsUrl = `${BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/crypto-prices`;
      
      try {
        pricesWs = new WebSocket(pricesWsUrl);
        
        pricesWs.onopen = () => {
          console.log('Connected to crypto prices WebSocket');
        };
        
        pricesWs.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'crypto_prices') {
              setCryptocurrencies(data.data);
              setIsLoading(false);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        pricesWs.onerror = (error) => {
          console.error('WebSocket error:', error);
          if (pricesWs) {
            pricesWs.close();
          }
        };
        
        pricesWs.onclose = () => {
          console.log('Crypto prices WebSocket closed. Reconnecting...');
          // Try to reconnect after 5 seconds
          reconnectTimeout = setTimeout(connectPricesWebSocket, 5000);
        };
      } catch (error) {
        console.error('Error setting up crypto prices WebSocket:', error);
        // Fallback to polling
        const interval = setInterval(fetchCryptocurrencies, 5000);
        return () => clearInterval(interval);
      }
    };

    const connectIndicatorsWebSocket = () => {
      const indicatorsWsUrl = `${BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/market-indicators`;
      
      try {
        indicatorsWs = new WebSocket(indicatorsWsUrl);
        
        indicatorsWs.onopen = () => {
          console.log('Connected to market indicators WebSocket');
        };
        
        indicatorsWs.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'market_indicators') {
              setMarketIndicators(data.data);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        indicatorsWs.onerror = (error) => {
          console.error('WebSocket error:', error);
          if (indicatorsWs) {
            indicatorsWs.close();
          }
        };
        
        indicatorsWs.onclose = () => {
          console.log('Market indicators WebSocket closed. Reconnecting...');
          // Try to reconnect after 5 seconds
          reconnectTimeout = setTimeout(connectIndicatorsWebSocket, 5000);
        };
      } catch (error) {
        console.error('Error setting up market indicators WebSocket:', error);
        // Fallback to polling
        const interval = setInterval(fetchMarketIndicators, 15000);
        return () => clearInterval(interval);
      }
    };

    // Connect to WebSockets
    connectPricesWebSocket();
    connectIndicatorsWebSocket();

    // Cleanup function
    return () => {
      if (pricesWs) {
        pricesWs.close();
      }
      if (indicatorsWs) {
        indicatorsWs.close();
      }
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

  const fetchChartData = async (symbol, interval) => {
    try {
      const response = await axios.get(`${API}/chart/${symbol}?interval=${interval}`);
      setChartData(response.data.candles);
    } catch (error) {
      console.error(`Error fetching chart data for ${symbol}:`, error);
    }
  };

  // Initialize chart when ref or data changes
  useEffect(() => {
    if (chartContainerRef.current && chartData.length > 0) {
      if (chartRef.current) {
        chartRef.current.remove();
        candlestickSeriesRef.current = null;
      }

      try {
        const chart = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: 400,
          layout: {
            background: { color: '#1E2030' },
            textColor: '#DDD',
          },
          grid: {
            vertLines: { color: '#262B43' },
            horzLines: { color: '#262B43' },
          },
          crosshair: {
            mode: CrosshairMode.Normal,
          },
          timeScale: {
            borderColor: '#454545',
            timeVisible: true,
          },
          rightPriceScale: {
            borderColor: '#454545',
          },
        });

        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#4CAF50',
          downColor: '#FF5252',
          borderVisible: false,
          wickUpColor: '#4CAF50',
          wickDownColor: '#FF5252',
        });

        candlestickSeriesRef.current = candlestickSeries;
        candlestickSeries.setData(chartData);

        // Handle resize
        const handleResize = () => {
          chart.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        };

        window.addEventListener('resize', handleResize);
        chartRef.current = chart;

        return () => {
          window.removeEventListener('resize', handleResize);
          if (chartRef.current) {
            chartRef.current.remove();
          }
        };
      } catch (error) {
        console.error('Error initializing chart:', error);
        // Create a fallback chart display
        if (chartContainerRef.current) {
          chartContainerRef.current.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full bg-slate-800 p-4">
              <p class="text-red-400 text-lg mb-4">Chart initialization error.</p>
              <p class="text-gray-300">Showing ${selectedCrypto} data for ${selectedTimeframe} timeframe</p>
              <div class="mt-4 w-full">
                <div class="w-full h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-11/12 h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-10/12 h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-full h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-9/12 h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-11/12 h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-10/12 h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-full h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-8/12 h-4 bg-slate-700 rounded mb-1"></div>
                <div class="w-11/12 h-4 bg-slate-700 rounded"></div>
              </div>
              <button 
                onClick={() => fetchChartData(selectedCrypto, selectedTimeframe)}
                class="mt-4 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded"
              >
                Retry Loading Chart
              </button>
            </div>
          `;
        }
      }
    }
  }, [chartData]);

  // Update chart data when selected crypto or timeframe changes
  useEffect(() => {
    fetchChartData(selectedCrypto, selectedTimeframe);
  }, [selectedCrypto, selectedTimeframe]);

  // Get fear and greed index color
  const getFearGreedColor = (index) => {
    if (index < 25) return 'text-red-500'; // Extreme Fear
    if (index < 40) return 'text-orange-500'; // Fear
    if (index < 60) return 'text-yellow-500'; // Neutral
    if (index < 75) return 'text-lime-500'; // Greed
    return 'text-green-500'; // Extreme Greed
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Navigation */}
      <header className="bg-slate-800 shadow-lg">
        <div className="container mx-auto py-4 px-6">
          <div className="flex justify-between items-center">
            <div className="text-2xl font-bold text-cyan-400">Crypto Dashboard</div>
            <nav className="hidden md:flex space-x-6">
              <a href="#" className="text-cyan-400 px-2 py-1 rounded">Dashboard</a>
              <a href="#" className="text-gray-300 hover:text-cyan-400 px-2 py-1 rounded">TrendScanner</a>
              <a href="#" className="text-gray-300 hover:text-cyan-400 px-2 py-1 rounded">Alerts</a>
              <a href="#" className="text-gray-300 hover:text-cyan-400 px-2 py-1 rounded">Strategy</a>
              <a href="#" className="text-gray-300 hover:text-cyan-400 px-2 py-1 rounded">Cointracker</a>
              <a href="#" className="text-gray-300 hover:text-cyan-400 px-2 py-1 rounded">Settings</a>
            </nav>
            <div className="flex items-center space-x-4">
              <button className="bg-slate-700 p-2 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center">
                <span className="font-bold">GP</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto py-6 px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Portfolio Value */}
          <div className="bg-slate-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-medium mb-4">Portfolio</h2>
            <div className="mb-4">
              <span className="text-4xl font-bold text-cyan-400">$48,932.15</span>
            </div>
            <div className="flex justify-end">
              <button className="bg-slate-700 hover:bg-slate-600 text-cyan-400 px-4 py-2 rounded-md">
                Details
              </button>
            </div>
          </div>

          {/* TrendScanner */}
          <div className="bg-slate-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-medium mb-4">TrendScanner</h2>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <FaBitcoin className="text-yellow-500 text-2xl" />
                <span className="text-lg">BTC</span>
              </div>
              <select
                className="bg-slate-700 text-white px-3 py-1 rounded-md"
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
              >
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
                <option value="1w">1w</option>
              </select>
            </div>
          </div>

          {/* Strategy */}
          <div className="bg-slate-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-medium mb-4">Strategy</h2>
            <div className="flex justify-center">
              <button className="bg-slate-700 hover:bg-slate-600 text-cyan-400 px-4 py-2 rounded-md">
                Guide
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Profit & Loss Chart */}
          <div className="bg-slate-800 rounded-lg shadow-lg p-6 lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-medium">Profit & Loss</h2>
              <span className="text-gray-400">Last 30 days</span>
            </div>
            <div className="h-64 relative">
              <svg className="w-full h-full" viewBox="0 0 400 200">
                <path
                  d="M0,200 L20,180 C40,160 80,120 120,110 C160,100 200,120 240,130 C280,140 320,140 360,120 L400,100 L400,200 L0,200 Z"
                  fill="url(#gradient)"
                  opacity="0.6"
                />
                <path
                  d="M0,200 L20,180 C40,160 80,120 120,110 C160,100 200,120 240,130 C280,140 320,140 360,120 L400,100"
                  fill="none"
                  stroke="url(#line-gradient)"
                  strokeWidth="3"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.7" />
                    <stop offset="100%" stopColor="#10B981" stopOpacity="0.1" />
                  </linearGradient>
                  <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#FCD34D" />
                    <stop offset="50%" stopColor="#10B981" />
                    <stop offset="100%" stopColor="#10B981" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-400 px-2">
                <span>Mar 2</span>
                <span>Mar 9</span>
                <span>Mar 15</span>
                <span>Mar 18</span>
              </div>
            </div>
          </div>

          {/* Strategy Maker */}
          <div className="bg-slate-800 rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-medium">Strategy Maker</h2>
            </div>
            <div className="flex justify-center my-8">
              <button className="bg-slate-700 hover:bg-slate-600 text-cyan-400 px-6 py-3 rounded-md">
                Scan
              </button>
            </div>
          </div>
        </div>

        {/* Market Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-slate-800 rounded-lg shadow-lg p-4">
            <h3 className="text-gray-400 mb-2">Total Market Cap</h3>
            <p className="text-2xl font-bold">
              {formatNumber(marketIndicators.total_market_cap)}
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg shadow-lg p-4">
            <h3 className="text-gray-400 mb-2">24h Volume</h3>
            <p className="text-2xl font-bold">
              {formatNumber(marketIndicators.total_volume_24h)}
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg shadow-lg p-4">
            <h3 className="text-gray-400 mb-2">BTC Dominance</h3>
            <p className="text-2xl font-bold">
              {marketIndicators.btc_dominance.toFixed(2)}%
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg shadow-lg p-4">
            <h3 className="text-gray-400 mb-2">Fear & Greed Index</h3>
            <p className={`text-2xl font-bold ${getFearGreedColor(marketIndicators.fear_greed_index)}`}>
              {marketIndicators.fear_greed_index}
            </p>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-slate-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-medium">Chart</h2>
              <div className="flex items-center space-x-2 bg-slate-700 px-3 py-1 rounded-md">
                {getCryptoIcon(selectedCrypto)}
                <select
                  className="bg-transparent text-white"
                  value={selectedCrypto}
                  onChange={(e) => setSelectedCrypto(e.target.value)}
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
            </div>
            <div className="flex space-x-2">
              <button 
                className={`px-3 py-1 rounded-md ${selectedTimeframe === '1h' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                onClick={() => setSelectedTimeframe('1h')}
              >
                1H
              </button>
              <button 
                className={`px-3 py-1 rounded-md ${selectedTimeframe === '4h' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                onClick={() => setSelectedTimeframe('4h')}
              >
                4H
              </button>
              <button 
                className={`px-3 py-1 rounded-md ${selectedTimeframe === '1d' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                onClick={() => setSelectedTimeframe('1d')}
              >
                1D
              </button>
              <button 
                className={`px-3 py-1 rounded-md ${selectedTimeframe === '1w' ? 'bg-cyan-600 text-white' : 'bg-slate-700 text-gray-300'}`}
                onClick={() => setSelectedTimeframe('1w')}
              >
                1W
              </button>
            </div>
          </div>
          <div ref={chartContainerRef} className="h-96 w-full" />
        </div>

        {/* Cryptocurrency Table */}
        <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden mb-6">
          <div className="p-6 border-b border-slate-700">
            <h2 className="text-xl font-medium">Cointracker</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-700">
              <thead className="bg-slate-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Coin
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Price
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                    24h Change
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Volume
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Market Cap
                  </th>
                </tr>
              </thead>
              <tbody className="bg-slate-800 divide-y divide-slate-700">
                {isLoading ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-4 text-center">Loading...</td>
                  </tr>
                ) : (
                  cryptocurrencies.map((crypto) => (
                    <tr 
                      key={crypto.symbol} 
                      className="hover:bg-slate-700 cursor-pointer"
                      onClick={() => setSelectedCrypto(crypto.symbol)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getCryptoIcon(crypto.symbol)}
                          <div className="ml-4">
                            <div className="text-sm font-medium">
                              {crypto.symbol.replace('USDT', '')}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        ${Number(crypto.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-right text-sm ${crypto.price_change_percentage_24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {crypto.price_change_percentage_24h >= 0 ? '+' : ''}{crypto.price_change_percentage_24h.toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        {formatNumber(crypto.volume_24h)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        {formatNumber(crypto.market_cap)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PortfolioProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </PortfolioProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
