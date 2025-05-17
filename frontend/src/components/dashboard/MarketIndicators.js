import React from 'react';

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

// Get fear and greed index color
const getFearGreedColor = (index) => {
  if (index < 25) return 'text-red-500'; // Extreme Fear
  if (index < 40) return 'text-orange-500'; // Fear
  if (index < 60) return 'text-yellow-500'; // Neutral
  if (index < 75) return 'text-lime-500'; // Greed
  return 'text-green-500'; // Extreme Greed
};

const MarketIndicator = ({ title, value, unit, change, icon }) => {
  const isPositive = change >= 0;
  const changeColor = isPositive ? 'text-green-500' : 'text-red-500';
  
  return (
    <div className="bg-slate-800 rounded-lg shadow-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-gray-400">{title}</h3>
        {icon && <span className="text-gray-300">{icon}</span>}
      </div>
      <p className="text-2xl font-bold mb-1">
        {unit === "USD" ? formatNumber(value) : `${value.toFixed(2)}${unit}`}
      </p>
      {change !== undefined && (
        <p className={`text-sm ${changeColor}`}>
          {isPositive ? '+' : ''}{change.toFixed(2)}% {isPositive ? '↑' : '↓'}
        </p>
      )}
    </div>
  );
};

const MarketIndicators = ({ indicators }) => {
  if (!indicators) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, index) => (
          <div key={index} className="bg-slate-800 rounded-lg shadow-lg p-4 animate-pulse">
            <div className="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-slate-700 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-slate-700 rounded w-1/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MarketIndicator 
        title="Total Market Cap" 
        value={indicators.total_market_cap || 0} 
        unit="USD" 
        change={indicators.total_market_cap_change_24h} 
        icon="📊"
      />
      <MarketIndicator 
        title="24h Volume" 
        value={indicators.total_volume_24h || 0} 
        unit="USD" 
        change={indicators.total_volume_change_24h} 
        icon="📈"
      />
      <MarketIndicator 
        title="BTC Dominance" 
        value={indicators.btc_dominance || 0} 
        unit="%" 
        change={indicators.btc_dominance_change_24h} 
        icon="₿"
      />
      <div className="bg-slate-800 rounded-lg shadow-lg p-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-gray-400">Fear & Greed Index</h3>
          <span className="text-gray-300">🧠</span>
        </div>
        <p className={`text-2xl font-bold mb-1 ${getFearGreedColor(indicators.fear_greed_index)}`}>
          {indicators.fear_greed_index || 0}
        </p>
        <p className="text-sm text-gray-400">
          {indicators.fear_greed_index < 25 ? 'Extreme Fear' :
           indicators.fear_greed_index < 40 ? 'Fear' :
           indicators.fear_greed_index < 60 ? 'Neutral' :
           indicators.fear_greed_index < 75 ? 'Greed' : 'Extreme Greed'}
        </p>
      </div>
    </div>
  );
};

export default MarketIndicators;