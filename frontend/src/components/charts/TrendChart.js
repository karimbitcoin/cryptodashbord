import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const TrendChart = ({ data, title, color = '#26a69a', height = 300 }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  
  useEffect(() => {
    if (chartContainerRef.current && data && data.length > 0) {
      // Clear any existing chart
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
      
      // Create the chart
      const chartOptions = {
        height: height,
        layout: {
          background: { color: 'rgba(15, 23, 42, 0)' },
          textColor: '#d1d5db',
        },
        grid: {
          vertLines: { color: 'rgba(42, 46, 57, 0.2)' },
          horzLines: { color: 'rgba(42, 46, 57, 0.2)' },
        },
        rightPriceScale: {
          borderColor: 'rgba(197, 203, 206, 0.4)',
        },
        timeScale: {
          borderColor: 'rgba(197, 203, 206, 0.4)',
          timeVisible: true,
        },
        crosshair: {
          mode: 0,
        },
        handleScroll: {
          mouseWheel: true,
          pressedMouseMove: true,
        },
        handleScale: {
          axisPressedMouseMove: true,
          mouseWheel: true,
          pinch: true,
        },
      };
      
      chartRef.current = createChart(chartContainerRef.current, chartOptions);
      
      // Add the area series
      const areaSeries = chartRef.current.addAreaSeries({
        topColor: `${color}80`, // With opacity
        bottomColor: `${color}00`, // Transparent
        lineColor: color,
        lineWidth: 2,
      });
      
      // Set the data
      areaSeries.setData(data);
      
      // Fit the visible range
      chartRef.current.timeScale().fitContent();
    }
    
    // Cleanup function
    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [data, color, height]);
  
  return (
    <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
      <h3 className="text-lg font-medium mb-4">{title}</h3>
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
};

export default TrendChart;