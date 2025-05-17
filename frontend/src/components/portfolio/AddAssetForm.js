import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AddAssetForm = ({ onAdd, onCancel }) => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [amount, setAmount] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [error, setError] = useState(null);

  // Fetch available cryptocurrencies
  useEffect(() => {
    const fetchCurrencies = async () => {
      try {
        const response = await axios.get(`${API}/cryptocurrencies`);
        setCurrencies(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching currencies:', error);
        setError('Failed to fetch available currencies');
        setLoading(false);
      }
    };

    fetchCurrencies();
  }, []);

  // Update current price when symbol changes
  useEffect(() => {
    if (currencies.length > 0) {
      const selected = currencies.find(c => c.symbol === symbol);
      if (selected) {
        setCurrentPrice(selected.price);
        setPurchasePrice(selected.price);
      }
    }
  }, [symbol, currencies]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!amount || !purchasePrice) {
      setError('All fields are required');
      return;
    }
    
    if (isNaN(amount) || isNaN(purchasePrice)) {
      setError('Amount and purchase price must be numbers');
      return;
    }
    
    if (parseFloat(amount) <= 0 || parseFloat(purchasePrice) <= 0) {
      setError('Amount and purchase price must be positive');
      return;
    }
    
    const asset = {
      symbol,
      amount: parseFloat(amount),
      purchase_price: parseFloat(purchasePrice),
      purchase_date: new Date()
    };
    
    onAdd(asset);
  };

  return (
    <div className="p-6 bg-slate-800 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-medium">Add New Asset</h2>
        <button 
          onClick={onCancel}
          className="p-2 bg-slate-700 hover:bg-slate-600 rounded-full"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-500 bg-opacity-20 border border-red-500 rounded-md text-red-500">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500"></div>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="symbol" className="block text-sm font-medium text-gray-300 mb-1">
                Cryptocurrency
              </label>
              <select
                id="symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="block w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-cyan-500 focus:border-cyan-500"
              >
                {currencies.map((currency) => (
                  <option key={currency.symbol} value={currency.symbol}>
                    {currency.symbol.replace('USDT', '')} (${currency.price.toFixed(2)})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label htmlFor="amount" className="block text-sm font-medium text-gray-300 mb-1">
                Amount
              </label>
              <input
                id="amount"
                type="number"
                step="any"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="block w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-cyan-500 focus:border-cyan-500"
                placeholder="Enter amount"
              />
            </div>
            
            <div>
              <label htmlFor="purchasePrice" className="flex justify-between text-sm font-medium text-gray-300 mb-1">
                <span>Purchase Price</span>
                <button
                  type="button"
                  onClick={() => setPurchasePrice(currentPrice.toString())}
                  className="text-xs text-cyan-400 hover:text-cyan-300"
                >
                  Use current: ${currentPrice.toFixed(2)}
                </button>
              </label>
              <input
                id="purchasePrice"
                type="number"
                step="any"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                className="block w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-cyan-500 focus:border-cyan-500"
                placeholder="Enter purchase price"
              />
            </div>
            
            <div className="pt-4 flex justify-end space-x-3">
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-md"
              >
                Add Asset
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

export default AddAssetForm;
