import React, { useEffect, useState } from 'react';
import { usePortfolio } from '../../contexts/PortfolioContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PortfolioView = () => {
  const { currentPortfolio, loading: portfolioLoading } = usePortfolio();
  const [currentPrices, setCurrentPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch current prices for portfolio assets
  useEffect(() => {
    const fetchPrices = async () => {
      if (!currentPortfolio) return;
      
      try {
        setLoading(true);
        const symbols = currentPortfolio.assets.map(asset => asset.symbol).join(',');
        const response = await axios.get(`${API}/cryptocurrencies?symbols=${symbols}`);
        
        // Create a map of symbol to price for easier access
        const priceMap = {};
        response.data.forEach(crypto => {
          priceMap[crypto.symbol] = crypto.price;
        });
        
        setCurrentPrices(priceMap);
        setError(null);
      } catch (error) {
        console.error('Error fetching current prices:', error);
        setError('Failed to fetch current prices');
      } finally {
        setLoading(false);
      }
    };
    
    if (currentPortfolio) {
      fetchPrices();
      
      // Set up interval to refresh prices
      const interval = setInterval(fetchPrices, 30000);
      return () => clearInterval(interval);
    }
  }, [currentPortfolio]);
  
  // Calculate portfolio stats
  const calculatePortfolioStats = () => {
    if (!currentPortfolio || Object.keys(currentPrices).length === 0) return null;
    
    let totalValue = 0;
    let totalCost = 0;
    
    const assetsWithValues = currentPortfolio.assets.map(asset => {
      const currentPrice = currentPrices[asset.symbol] || 0;
      const value = asset.amount * currentPrice;
      const cost = asset.amount * asset.purchase_price;
      const profitLoss = value - cost;
      const profitLossPercentage = cost > 0 ? (profitLoss / cost) * 100 : 0;
      
      totalValue += value;
      totalCost += cost;
      
      return {
        ...asset,
        currentPrice,
        value,
        cost,
        profitLoss,
        profitLossPercentage
      };
    });
    
    const totalProfitLoss = totalValue - totalCost;
    const totalProfitLossPercentage = totalCost > 0 ? (totalProfitLoss / totalCost) * 100 : 0;
    
    return {
      totalValue,
      totalCost,
      totalProfitLoss,
      totalProfitLossPercentage,
      assets: assetsWithValues
    };
  };
  
  const portfolioStats = calculatePortfolioStats();
  
  // Format numbers
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };
  
  const formatPercentage = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100);
  };
  
  if (portfolioLoading || loading) {
    return (
      <div className="p-6 bg-slate-800 rounded-lg shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-medium">Portfolio</h2>
          <div className="flex space-x-2">
            <div className="w-4 h-4 bg-slate-600 rounded-full animate-pulse"></div>
            <div className="w-4 h-4 bg-slate-600 rounded-full animate-pulse"></div>
            <div className="w-4 h-4 bg-slate-600 rounded-full animate-pulse"></div>
          </div>
        </div>
        <div className="h-64 flex items-center justify-center">
          <div className="text-gray-400">Loading portfolio data...</div>
        </div>
      </div>
    );
  }
  
  if (!currentPortfolio) {
    return (
      <div className="p-6 bg-slate-800 rounded-lg shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-medium">Portfolio</h2>
        </div>
        <div className="h-64 flex flex-col items-center justify-center">
          <div className="text-gray-400 mb-4">No portfolio found</div>
          <button className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-md">
            Create Portfolio
          </button>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-6 bg-slate-800 rounded-lg shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-medium">Portfolio</h2>
        </div>
        <div className="bg-red-500 bg-opacity-20 border border-red-500 rounded-md p-4 text-red-500">
          {error}
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-6 bg-slate-800 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-medium">{currentPortfolio.name}</h2>
        <div className="flex space-x-2">
          <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <button className="p-2 bg-slate-700 hover:bg-slate-600 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </button>
        </div>
      </div>
      
      {portfolioStats && (
        <div className="mb-6">
          <div className="mb-2">
            <span className="text-4xl font-bold text-cyan-400">
              {formatCurrency(portfolioStats.totalValue)}
            </span>
          </div>
          <div className={`text-sm ${portfolioStats.totalProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {portfolioStats.totalProfitLoss >= 0 ? '+' : ''}
            {formatCurrency(portfolioStats.totalProfitLoss)} ({formatPercentage(portfolioStats.totalProfitLossPercentage)})
          </div>
        </div>
      )}
      
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-400 mb-2">ASSETS</h3>
        <div className="space-y-4">
          {portfolioStats?.assets.map((asset) => (
            <div key={asset.symbol} className="flex justify-between items-center p-3 bg-slate-700 rounded-md">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  {asset.symbol.slice(0, 1)}
                </div>
                <div>
                  <div className="font-medium">{asset.symbol.replace('USDT', '')}</div>
                  <div className="text-xs text-gray-400">{asset.amount} coins</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium">{formatCurrency(asset.value)}</div>
                <div className={`text-xs ${asset.profitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {asset.profitLoss >= 0 ? '+' : ''}
                  {formatPercentage(asset.profitLossPercentage)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PortfolioView;
