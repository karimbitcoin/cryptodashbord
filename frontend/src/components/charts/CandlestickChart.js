import React, { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CandlestickChart = ({ symbol, timeframe, height = 400, showToolbar = true }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const sma7SeriesRef = useRef(null);
  const sma25SeriesRef = useRef(null);

  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSMA7, setShowSMA7] = useState(true);
  const [showSMA25, setShowSMA25] = useState(true);
  const [showVolume, setShowVolume] = useState(true);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(`${API}/crypto/chart/${symbol}?interval=${timeframe}`);
        setChartData(response.data);
        setError(null);
        setIsLoading(false);
      } catch (error) {
        console.error(`Error fetching chart data for ${symbol}:`, error);
        setError(`Failed to load chart data for ${symbol}`);
        setIsLoading(false);
      }
    };

    fetchChartData();
  }, [symbol, timeframe]);

  useEffect(() => {
    if (chartContainerRef.current && chartData.candles && chartData.candles.length > 0) {
      // Remove previous chart if it exists
      if (chartRef.current) {
        chartRef.current.remove();
        candlestickSeriesRef.current = null;
        volumeSeriesRef.current = null;
        sma7SeriesRef.current = null;
        sma25SeriesRef.current = null;
      }

      try {
        // Create new chart
        const chart = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: height,
          layout: {
            background: { color: '#1E293B' }, // slate-800
            textColor: '#E2E8F0', // slate-200
          },
          grid: {
            vertLines: { color: '#334155' }, // slate-700
            horzLines: { color: '#334155' }, // slate-700
          },
          crosshair: {
            mode: CrosshairMode.Normal,
          },
          timeScale: {
            borderColor: '#475569', // slate-600
            timeVisible: true,
            secondsVisible: false,
          },
          rightPriceScale: {
            borderColor: '#475569', // slate-600
          },
        });

        // Add candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#10B981', // emerald-500
          downColor: '#EF4444', // red-500
          borderUpColor: '#10B981', // emerald-500
          borderDownColor: '#EF4444', // red-500
          wickUpColor: '#10B981', // emerald-500
          wickDownColor: '#EF4444', // red-500
        });

        // Format candle data
        const formattedCandles = chartData.candles.map(candle => ({
          time: new Date(candle.timestamp).getTime() / 1000,
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
          value: candle.volume,
        }));

        candlestickSeries.setData(formattedCandles);
        candlestickSeriesRef.current = candlestickSeries;

        // Add volume series if available
        if (showVolume && formattedCandles.length > 0) {
          const volumeSeries = chart.addHistogramSeries({
            color: '#6366F1', // indigo-500
            priceFormat: {
              type: 'volume',
            },
            priceScaleId: 'volume',
            scaleMargins: {
              top: 0.8,
              bottom: 0,
            },
          });
          
          volumeSeries.setData(formattedCandles);
          volumeSeriesRef.current = volumeSeries;
        }

        // Add SMA 7 if available and enabled
        if (showSMA7 && chartData.indicators && chartData.indicators.sma_7) {
          const sma7Series = chart.addLineSeries({
            color: '#3B82F6', // blue-500
            lineWidth: 2,
            priceLineVisible: false,
          });

          const sma7Data = chartData.indicators.sma_7
            .map((value, index) => ({
              time: formattedCandles[index]?.time,
              value: value,
            }))
            .filter(item => item.time && item.value !== null);

          sma7Series.setData(sma7Data);
          sma7SeriesRef.current = sma7Series;
        }

        // Add SMA 25 if available and enabled
        if (showSMA25 && chartData.indicators && chartData.indicators.sma_25) {
          const sma25Series = chart.addLineSeries({
            color: '#EC4899', // pink-500
            lineWidth: 2,
            priceLineVisible: false,
          });

          const sma25Data = chartData.indicators.sma_25
            .map((value, index) => ({
              time: formattedCandles[index]?.time,
              value: value,
            }))
            .filter(item => item.time && item.value !== null);

          sma25Series.setData(sma25Data);
          sma25SeriesRef.current = sma25Series;
        }

        // Handle window resize
        const handleResize = () => {
          chart.applyOptions({
            width: chartContainerRef.current.clientWidth,
          });
        };

        window.addEventListener('resize', handleResize);
        chartRef.current = chart;

        // Cleanup
        return () => {
          window.removeEventListener('resize', handleResize);
          if (chartRef.current) {
            chartRef.current.remove();
          }
        };
      } catch (error) {
        console.error('Error initializing chart:', error);
        setError('Failed to initialize chart. Please try again later.');
      }
    }
  }, [chartData, height, showSMA7, showSMA25, showVolume]);

  // Toggle indicators
  const toggleSMA7 = () => {
    setShowSMA7(!showSMA7);
  };

  const toggleSMA25 = () => {
    setShowSMA25(!showSMA25);
  };

  const toggleVolume = () => {
    setShowVolume(!showVolume);
  };

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-800 rounded-lg p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-800 rounded-lg p-4">
        <p className="text-red-400 text-lg mb-4">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-md"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="w-full">
      {showToolbar && (
        <div className="flex justify-end space-x-2 mb-2">
          <button 
            className={`px-3 py-1 rounded-md text-sm ${showSMA7 ? 'bg-blue-500 text-white' : 'bg-slate-700 text-gray-300'}`}
            onClick={toggleSMA7}
          >
            SMA 7
          </button>
          <button 
            className={`px-3 py-1 rounded-md text-sm ${showSMA25 ? 'bg-pink-500 text-white' : 'bg-slate-700 text-gray-300'}`}
            onClick={toggleSMA25}
          >
            SMA 25
          </button>
          <button 
            className={`px-3 py-1 rounded-md text-sm ${showVolume ? 'bg-indigo-500 text-white' : 'bg-slate-700 text-gray-300'}`}
            onClick={toggleVolume}
          >
            Volume
          </button>
        </div>
      )}
      <div ref={chartContainerRef} className="w-full" style={{ height: `${height}px` }} />
    </div>
  );
};

export default CandlestickChart;