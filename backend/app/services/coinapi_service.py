import os
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# CoinAPI base URL
COINAPI_BASE_URL = "https://rest.coinapi.io/v1"

# API key from environment variables
COINAPI_KEY = os.environ.get("COINAPI_KEY", "52d3f36d-bdb3-4653-86c3-08284eeeed63")

def get_historical_data(
    symbol: str, 
    period_id: str = "1DAY",
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data from CoinAPI
    
    Args:
        symbol: Symbol in format like "BTC" or "ETH"
        period_id: Time period (e.g., "1HRS", "1DAY", "1MTH")
        limit: Maximum number of data points to return
        start_time: Start time for data (ISO format)
        end_time: End time for data (ISO format)
        
    Returns:
        List of OHLCV data points
    """
    # Check if api key is available
    if not COINAPI_KEY:
        logger.warning("CoinAPI key not found, using mock data")
        return []
    
    # Prepare query parameters
    params = {"limit": limit}
    
    if start_time:
        params["time_start"] = start_time.isoformat()
    if end_time:
        params["time_end"] = end_time.isoformat()
    
    # Prepare headers with API key
    headers = {"X-CoinAPI-Key": COINAPI_KEY}
    
    try:
        # Make the API call
        response = requests.get(
            f"{COINAPI_BASE_URL}/ohlcv/{symbol}/USD/history",
            params=params,
            headers=headers
        )
        
        # Check response status
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"CoinAPI error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error calling CoinAPI: {e}")
        return []

def get_exchange_rates(base_currency: str = "USD", symbols: List[str] = None) -> Dict[str, float]:
    """
    Get current exchange rates for cryptocurrencies
    
    Args:
        base_currency: Base currency (e.g., "USD", "EUR")
        symbols: List of cryptocurrency symbols (e.g., ["BTC", "ETH"])
        
    Returns:
        Dictionary mapping symbols to exchange rates
    """
    # If no symbols provided, use default list
    if not symbols:
        symbols = ["BTC", "ETH", "SOL", "BNB", "ADA", "XRP"]
    
    # Check if api key is available
    if not COINAPI_KEY:
        logger.warning("CoinAPI key not found, using mock data")
        return {symbol: 0.0 for symbol in symbols}
    
    # Prepare headers with API key
    headers = {"X-CoinAPI-Key": COINAPI_KEY}
    
    try:
        # Make the API call for each symbol
        rates = {}
        for symbol in symbols:
            response = requests.get(
                f"{COINAPI_BASE_URL}/exchangerate/{symbol}/{base_currency}",
                headers=headers
            )
            
            # Check response status
            if response.status_code == 200:
                data = response.json()
                rates[symbol] = data.get("rate", 0.0)
            else:
                logger.error(f"CoinAPI error for {symbol}: {response.status_code} - {response.text}")
                rates[symbol] = 0.0
                
        return rates
        
    except Exception as e:
        logger.error(f"Error calling CoinAPI: {e}")
        return {symbol: 0.0 for symbol in symbols}

def get_technical_indicators(symbol: str, period: str = "1d", indicator: str = "sma") -> Dict[str, Any]:
    """
    Get technical indicators for a symbol
    
    This is a mock implementation since CoinAPI doesn't directly provide technical indicators.
    In a real implementation, you'd either:
    1. Get the OHLCV data and calculate indicators yourself
    2. Use another API that provides technical indicators
    
    Args:
        symbol: Cryptocurrency symbol
        period: Time period
        indicator: Indicator type (sma, ema, etc.)
        
    Returns:
        Dictionary with indicator values
    """
    # Mock implementation
    if indicator == "sma":
        return {
            "symbol": symbol,
            "indicator": "sma",
            "periods": [7, 25, 99],
            "values": {
                "7": [100.0, 101.5, 102.3, 101.8, 103.2],
                "25": [98.5, 99.2, 100.1, 101.0, 101.8],
                "99": [95.0, 96.2, 97.5, 98.3, 99.7]
            }
        }
    elif indicator == "ema":
        return {
            "symbol": symbol,
            "indicator": "ema",
            "periods": [7, 25, 99],
            "values": {
                "7": [100.2, 101.7, 102.5, 102.0, 103.4],
                "25": [98.7, 99.4, 100.3, 101.2, 102.0],
                "99": [95.2, 96.4, 97.7, 98.5, 99.9]
            }
        }
    else:
        return {
            "symbol": symbol,
            "indicator": indicator,
            "error": "Indicator not supported"
        }
