import React from 'react';

const FearGreedIndex = ({ value }) => {
  // Determine gauge position and colors based on value
  const getGaugeColor = (value) => {
    if (value <= 20) return 'bg-red-500'; // Extreme Fear
    if (value <= 40) return 'bg-orange-500'; // Fear
    if (value <= 60) return 'bg-yellow-500'; // Neutral
    if (value <= 80) return 'bg-green-500'; // Greed
    return 'bg-emerald-500'; // Extreme Greed
  };

  const getGaugeSentiment = (value) => {
    if (value <= 20) return 'Extreme Fear';
    if (value <= 40) return 'Fear';
    if (value <= 60) return 'Neutral';
    if (value <= 80) return 'Greed';
    return 'Extreme Greed';
  };

  // Calculate rotation for the needle
  const rotation = value ? (value / 100) * 180 - 90 : -90;

  return (
    <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-medium mb-4">Fear & Greed Index</h3>
      
      <div className="relative w-full h-32 mb-4">
        {/* Semi-circle gauge */}
        <div className="absolute bottom-0 w-full h-full overflow-hidden">
          <div className="relative w-full h-full">
            {/* Gauge background */}
            <div className="absolute bottom-0 w-full h-[50%] rounded-t-full bg-gradient-to-r from-red-500 via-yellow-500 to-emerald-500 overflow-hidden"></div>
            
            {/* Current value marker */}
            <div 
              className="absolute bottom-0 left-1/2 w-1 h-[50%] bg-white origin-bottom z-10 transform -translate-x-1/2"
              style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
            >
              <div className="w-3 h-3 rounded-full bg-white absolute -top-1 -left-1"></div>
            </div>
            
            {/* Value labels */}
            <div className="absolute bottom-0 w-full flex justify-between px-4 text-xs text-white">
              <span>0</span>
              <span>25</span>
              <span>50</span>
              <span>75</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <div className="flex justify-center items-center mb-2">
          <div className={`w-4 h-4 rounded-full ${getGaugeColor(value)} mr-2`}></div>
          <div className="text-lg font-bold">{value || '?'}</div>
        </div>
        <div className="text-sm text-gray-400">{getGaugeSentiment(value)}</div>
      </div>
    </div>
  );
};

export default FearGreedIndex;