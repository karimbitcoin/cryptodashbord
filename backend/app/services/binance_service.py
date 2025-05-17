import os
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from binance.client import Client

from app.core.models import CryptoCurrency, MarketIndicator, ChartData

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Binance client 
try:
    api_key = os.environ.get("BINANCE_API_KEY", "")
    api_secret = os.environ.get("BINANCE_API_SECRET", "")
    binance_client = Client(api_key, api_secret)
    # Test API connection
    binance_client.get_system_status()
except Exception as e:
    logger.warning(f"Failed to connect to Binance API: {e}")
    logger.warning("Using mock data instead")
    binance_client = None

# Mock data for testing when API is not available
MOCK_CRYPTOCURRENCIES = [
    {"symbol": "BTC", "name": "Bitcoin", "price": 58750.42, "change_24h": 2.5, "volume_24h": 32500000000, "market_cap": 1123000000000},
    {"symbol": "ETH", "name": "Ethereum", "price": 3890.15, "change_24h": 1.8, "volume_24h": 18600000000, "market_cap": 465000000000},
    {"symbol": "SOL", "name": "Solana", "price": 135.67, "change_24h": 5.2, "volume_24h": 5700000000, "market_cap": 48000000000},
    {"symbol": "BNB", "name": "Binance Coin", "price": 425.30, "change_24h": -0.7, "volume_24h": 2800000000, "market_cap": 70000000000},
    {"symbol": "ADA", "name": "Cardano", "price": 1.24, "change_24h": -1.5, "volume_24h": 1950000000, "market_cap": 41500000000},
    {"symbol": "DOT", "name": "Polkadot", "price": 18.35, "change_24h": 3.1, "volume_24h": 980000000, "market_cap": 19800000000},
    {"symbol": "XRP", "name": "Ripple", "price": 0.72, "change_24h": -0.3, "volume_24h": 2100000000, "market_cap": 34500000000},
    {"symbol": "DOGE", "name": "Dogecoin", "price": 0.14, "change_24h": 4.2, "volume_24h": 1500000000, "market_cap": 18500000000},
    {"symbol": "AVAX", "name": "Avalanche", "price": 29.85, "change_24h": 2.8, "volume_24h": 750000000, "market_cap": 10200000000},
    {"symbol": "MATIC", "name": "Polygon", "price": 1.05, "change_24h": 1.3, "volume_24h": 850000000, "market_cap": 9500000000},
    {"symbol": "LINK", "name": "Chainlink", "price": 14.28, "change_24h": -0.5, "volume_24h": 620000000, "market_cap": 7800000000},
    {"symbol": "UNI", "name": "Uniswap", "price": 9.45, "change_24h": -1.2, "volume_24h": 380000000, "market_cap": 5900000000},
    {"symbol": "ATOM", "name": "Cosmos", "price": 12.85, "change_24h": 3.7, "volume_24h": 410000000, "market_cap": 4500000000},
    {"symbol": "NEAR", "name": "NEAR Protocol", "price": 5.32, "change_24h": 2.1, "volume_24h": 280000000, "market_cap": 4200000000},
    {"symbol": "ALGO", "name": "Algorand", "price": 0.38, "change_24h": 0.9, "volume_24h": 150000000, "market_cap": 2800000000},
    {"symbol": "FTM", "name": "Fantom", "price": 0.82, "change_24h": 4.5, "volume_24h": 210000000, "market_cap": 2100000000},
    {"symbol": "OP", "name": "Optimism", "price": 2.68, "change_24h": 5.8, "volume_24h": 310000000, "market_cap": 2500000000},
    {"symbol": "ARB", "name": "Arbitrum", "price": 1.35, "change_24h": 3.2, "volume_24h": 290000000, "market_cap": 1950000000},
    {"symbol": "SUI", "name": "Sui", "price": 1.62, "change_24h": 7.4, "volume_24h": 380000000, "market_cap": 1850000000},
    {"symbol": "APT", "name": "Aptos", "price": 8.75, "change_24h": 2.8, "volume_24h": 250000000, "market_cap": 1650000000}
]

MOCK_MARKET_INDICATORS = [
    {"name": "Total Market Cap", "value": 2350000000000, "change_24h": 1.8, "unit": "USD"},
    {"name": "Total 24h Volume", "value": 95000000000, "change_24h": 3.2, "unit": "USD"},
    {"name": "BTC Dominance", "value": 47.5, "change_24h": -0.3, "unit": "%"},
    {"name": "ETH Dominance", "value": 18.2, "change_24h": 0.2, "unit": "%"},
    {"name": "Fear & Greed Index", "value": 65, "change_24h": 5, "unit": "score"}
]

def generate_mock_chart_data(symbol: str, interval: str, limit: int, 
                            start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    # Base price depends on the symbol
    base_price = next((crypto["price"] for crypto in MOCK_CRYPTOCURRENCIES 
                      if crypto["symbol"] == symbol), 100.0)
    
    # Generate time series data
    date_list = []
    current = start_time
    while current <= end_time and len(date_list) < limit:
        date_list.append(current)
        # Interval determines the time step
        if interval == '1m':
            current += timedelta(minutes=1)
        elif interval == '5m':
            current += timedelta(minutes=5)
        elif interval == '15m':
            current += timedelta(minutes=15)
        elif interval == '30m':
            current += timedelta(minutes=30)
        elif interval == '1h':
            current += timedelta(hours=1)
        elif interval == '2h':
            current += timedelta(hours=2)
        elif interval == '4h':
            current += timedelta(hours=4)
        elif interval == '6h':
            current += timedelta(hours=6)
        elif interval == '8h':
            current += timedelta(hours=8)
        elif interval == '12h':
            current += timedelta(hours=12)
        elif interval == '1d':
            current += timedelta(days=1)
        elif interval == '3d':
            current += timedelta(days=3)
        elif interval == '1w':
            current += timedelta(weeks=1)
        elif interval == '1M':
            # Approximate month as 30 days
            current += timedelta(days=30)
        else:
            current += timedelta(days=1)
    
    # Generate OHLCV data
    candles = []
    volatility = base_price * 0.02  # 2% of base price
    
    current_price = base_price
    for i, timestamp in enumerate(date_list):
        # Add some randomness for realistic price movement
        price_change = random.uniform(-volatility, volatility)
        
        # Generate OHLCV values
        open_price = current_price
        high_price = open_price + abs(price_change) * random.uniform(0.5, 1.5)
        low_price = open_price - abs(price_change) * random.uniform(0.5, 1.5)
        close_price = open_price + price_change
        
        # Make sure high is always highest and low is always lowest
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Volume varies with price change magnitude
        volume = base_price * 100 * (1 + abs(price_change/base_price) * 10)
        
        candles.append({
            "timestamp": timestamp.isoformat(),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": round(volume, 2)
        })
        
        current_price = close_price
    
    # Calculate some basic technical indicators
    close_prices = [candle["close"] for candle in candles]
    
    # Simple Moving Averages
    sma_7 = calculate_sma(close_prices, 7)
    sma_25 = calculate_sma(close_prices, 25)
    
    return {
        "symbol": symbol,
        "interval": interval,
        "candles": candles,
        "indicators": {
            "sma_7": sma_7,
            "sma_25": sma_25
        }
    }

def calculate_sma(prices, window):
    """Calculate Simple Moving Average"""
    if len(prices) < window:
        return [None] * len(prices)
    
    result = [None] * (window - 1)
    for i in range(len(prices) - window + 1):
        result.append(sum(prices[i:i+window]) / window)
    
    return result

def get_crypto_data(limit: int = 20) -> List[CryptoCurrency]:
    """Get cryptocurrency data from Binance API or mock data"""
    if binance_client:
        try:
            # Get all tickers
            tickers = binance_client.get_ticker()
            # Get 24h ticker statistics
            ticker_24h = {t['symbol']: t for t in binance_client.get_ticker()}
            
            # Filter for USDT pairs and sort by volume
            usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT')]
            usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
            
            # Take top N pairs
            top_pairs = usdt_pairs[:limit]
            
            # Format data
            result = []
            for pair in top_pairs:
                symbol = pair['symbol'].replace('USDT', '')
                price = float(pair['lastPrice'])
                change_24h = float(pair['priceChangePercent'])
                volume_24h = float(pair['quoteVolume'])
                
                # For market cap, we would need additional data from another API
                # Here we're estimating based on circulating supply * price
                # This is just an approximation for demonstration
                market_cap = price * 1000000  # Placeholder
                
                result.append({
                    "symbol": symbol,
                    "name": symbol,  # Would need another API to get full names
                    "price": price,
                    "change_24h": change_24h,
                    "volume_24h": volume_24h,
                    "market_cap": market_cap
                })
                
            return result
            
        except Exception as e:
            logger.warning(f"Error fetching crypto data from Binance: {e}")
            logger.warning("Using mock data instead")
    
    # Return mock data if Binance API is not available or fails
    return MOCK_CRYPTOCURRENCIES[:limit]

def get_market_indicators() -> List[MarketIndicator]:
    """Get market indicators like total market cap, trading volume, Bitcoin dominance"""
    # In a real implementation, these would come from an API
    # For this demo, we'll use mock data
    return MOCK_MARKET_INDICATORS

def get_chart_data(
    symbol: str, 
    interval: str = "1d", 
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> ChartData:
    """Get chart data for a specific cryptocurrency"""
    if not start_time:
        start_time = datetime.now() - timedelta(days=30)
    if not end_time:
        end_time = datetime.now()
        
    if binance_client:
        try:
            # Convert interval from our API format to Binance format
            # Binance uses the same format as our API, so no conversion needed
            
            # Convert datetime to milliseconds timestamp
            start_ms = int(start_time.timestamp() * 1000)
            end_ms = int(end_time.timestamp() * 1000)
            
            # Get klines (candlestick data)
            klines = binance_client.get_klines(
                symbol=f"{symbol}USDT",
                interval=interval,
                startTime=start_ms,
                endTime=end_ms,
                limit=limit
            )
            
            # Convert to our format
            candles = []
            for k in klines:
                timestamp = datetime.fromtimestamp(k[0] / 1000)
                candles.append({
                    "timestamp": timestamp.isoformat(),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                })
                
            # Calculate technical indicators
            if candles:
                closes = [c["close"] for c in candles]
                sma_7 = calculate_sma(closes, 7)
                sma_25 = calculate_sma(closes, 25)
                
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "candles": candles,
                    "indicators": {
                        "sma_7": sma_7,
                        "sma_25": sma_25
                    }
                }
            else:
                # If no data returned, use mock data
                logger.warning(f"No chart data returned from Binance for {symbol}, using mock data")
                return generate_mock_chart_data(symbol, interval, limit, start_time, end_time)
                
        except Exception as e:
            logger.warning(f"Error fetching chart data from Binance: {e}")
            logger.warning("Using mock data instead")
    
    # Return mock data if Binance API is not available or fails
    return generate_mock_chart_data(symbol, interval, limit, start_time, end_time)
