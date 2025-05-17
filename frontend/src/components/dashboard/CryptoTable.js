import React, { useState } from 'react';
import { FaBitcoin, FaEthereum } from 'react-icons/fa';
import { SiCardano, SiLitecoin, SiDogecoin, SiBinance, SiSolana } from 'react-icons/si';

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

const CryptoTable = ({ cryptocurrencies, isLoading, onSelectCrypto }) => {
  const [sortConfig, setSortConfig] = useState({
    key: 'market_cap',
    direction: 'desc'
  });
  const [searchTerm, setSearchTerm] = useState('');

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortDirection = (key) => {
    if (sortConfig.key === key) {
      return sortConfig.direction === 'asc' ? '↑' : '↓';
    }
    return '';
  };

  // Filter and sort cryptocurrencies
  const filteredAndSortedCryptos = [...(cryptocurrencies || [])]
    .filter(crypto => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return crypto.symbol.toLowerCase().includes(term) || 
             (crypto.name && crypto.name.toLowerCase().includes(term));
    })
    .sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (a[sortConfig.key] > b[sortConfig.key]) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

  return (
    <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
      <div className="p-6 border-b border-slate-700">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center">
          <h2 className="text-xl font-medium mb-4 md:mb-0">Cryptocurrency Market</h2>
          <div className="relative">
            <input
              type="text"
              placeholder="Search coins..."
              className="w-full md:w-64 bg-slate-700 text-white rounded-md px-4 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="absolute right-3 top-2 text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-700">
          <thead className="bg-slate-700">
            <tr>
              <th 
                scope="col" 
                className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                onClick={() => requestSort('name')}
              >
                Coin {getSortDirection('name')}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                onClick={() => requestSort('price')}
              >
                Price {getSortDirection('price')}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                onClick={() => requestSort('change_24h')}
              >
                24h Change {getSortDirection('change_24h')}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                onClick={() => requestSort('volume_24h')}
              >
                Volume {getSortDirection('volume_24h')}
              </th>
              <th 
                scope="col" 
                className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer"
                onClick={() => requestSort('market_cap')}
              >
                Market Cap {getSortDirection('market_cap')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-slate-800 divide-y divide-slate-700">
            {isLoading ? (
              [...Array(10)].map((_, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-slate-700 rounded-full animate-pulse"></div>
                      <div className="space-y-2">
                        <div className="h-4 w-20 bg-slate-700 rounded animate-pulse"></div>
                        <div className="h-3 w-16 bg-slate-700 rounded animate-pulse"></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="h-4 w-24 bg-slate-700 rounded animate-pulse ml-auto"></div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="h-4 w-16 bg-slate-700 rounded animate-pulse ml-auto"></div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="h-4 w-24 bg-slate-700 rounded animate-pulse ml-auto"></div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="h-4 w-28 bg-slate-700 rounded animate-pulse ml-auto"></div>
                  </td>
                </tr>
              ))
            ) : filteredAndSortedCryptos.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-400">
                  No cryptocurrencies found matching "{searchTerm}"
                </td>
              </tr>
            ) : (
              filteredAndSortedCryptos.map((crypto) => (
                <tr 
                  key={crypto.symbol} 
                  className="hover:bg-slate-700 cursor-pointer transition-colors duration-150"
                  onClick={() => onSelectCrypto && onSelectCrypto(crypto.symbol)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getCryptoIcon(crypto.symbol)}
                      <div className="ml-4">
                        <div className="text-sm font-medium text-white">
                          {crypto.symbol.replace('USDT', '')}
                        </div>
                        <div className="text-sm text-gray-400">
                          {crypto.name || crypto.symbol}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    ${Number(crypto.price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-right text-sm ${crypto.change_24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {crypto.change_24h >= 0 ? '+' : ''}{crypto.change_24h.toFixed(2)}%
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
  );
};

export default CryptoTable;