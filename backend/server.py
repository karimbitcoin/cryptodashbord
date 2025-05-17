from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import json
from binance.client import Client
import websockets
import requests
import redis
import pandas as pd

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Binance API configuration
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')

# Initialize Binance client
binance_client = None
using_mock_data = False

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    binance_client.ping()  # Check if API is accessible
    logger.info("Binance API connected successfully")
except Exception as e:
    logger.warning(f"Failed to connect to Binance API: {e}")
    logger.warning("Using mock data instead")
    using_mock_data = True

# Redis client for caching
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()  # Check if Redis is available
    logger.info("Redis connected successfully")
except redis.ConnectionError:
    redis_client = None
    logger.warning("Redis not available, caching will be disabled")

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

# Models
class CryptoCurrency(BaseModel):
    symbol: str
    price: float
    price_change_24h: float
    price_change_percentage_24h: float
    volume_24h: float
    market_cap: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Portfolio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_value: float
    currencies: List[Dict[str, Any]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class MarketIndicator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_market_cap: float
    total_volume_24h: float
    btc_dominance: float
    eth_dominance: float
    fear_greed_index: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ChartData(BaseModel):
    symbol: str
    interval: str
    candles: List[Dict[str, Any]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Helper Functions
async def get_crypto_prices(symbols: List[str] = None):
    """Fetch current prices for cryptocurrencies from Binance API"""
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "DOTUSDT"]
    
    result = []
    try:
        # Check if data is in Redis cache
        cache_key = f"crypto_prices:{'-'.join(symbols)}"
        cached_data = redis_client.get(cache_key) if redis_client else None
        
        if cached_data:
            return json.loads(cached_data)
        
        # Get tickers from Binance
        tickers = binance_client.get_ticker()
        symbol_data = {ticker['symbol']: ticker for ticker in tickers}
        
        for symbol in symbols:
            if symbol in symbol_data:
                ticker = symbol_data[symbol]
                
                # Get 24h price change
                day_stats = binance_client.get_ticker(symbol=symbol)
                
                # Calculate market cap (approximation)
                # This is simplified; actual market cap would require total supply data
                current_price = float(ticker['lastPrice'])
                volume_24h = float(ticker['volume'])
                
                result.append({
                    "symbol": symbol,
                    "price": current_price,
                    "price_change_24h": float(day_stats['priceChange']),
                    "price_change_percentage_24h": float(day_stats['priceChangePercent']),
                    "volume_24h": volume_24h,
                    "market_cap": current_price * volume_24h * 0.1,  # Simple approximation
                    "last_updated": datetime.utcnow().isoformat()
                })
                
        # Cache the result in Redis for 30 seconds
        if redis_client:
            redis_client.setex(cache_key, 30, json.dumps(result))
            
        return result
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return []

async def get_market_indicators():
    """Fetch overall market indicators"""
    try:
        # Try to get from cache
        cache_key = "market_indicators"
        cached_data = redis_client.get(cache_key) if redis_client else None
        
        if cached_data:
            return json.loads(cached_data)
        
        # Get global market data (simplified)
        total_market_cap = 0
        total_volume = 0
        
        # Get BTC market cap
        btc_ticker = binance_client.get_ticker(symbol="BTCUSDT")
        btc_price = float(btc_ticker['lastPrice'])
        btc_volume = float(btc_ticker['volume'])
        btc_market_cap = btc_price * btc_volume * 0.1  # Simple approximation
        
        # Get ETH market cap
        eth_ticker = binance_client.get_ticker(symbol="ETHUSDT")
        eth_price = float(eth_ticker['lastPrice'])
        eth_volume = float(eth_ticker['volume'])
        eth_market_cap = eth_price * eth_volume * 0.1  # Simple approximation
        
        # Get global data (simple approximation)
        tickers = binance_client.get_ticker()
        for ticker in tickers:
            if ticker['symbol'].endswith('USDT'):
                price = float(ticker['lastPrice'])
                volume = float(ticker['volume'])
                market_cap = price * volume * 0.1  # Simple approximation
                total_market_cap += market_cap
                total_volume += volume
        
        # Calculate dominance
        btc_dominance = (btc_market_cap / total_market_cap) * 100 if total_market_cap > 0 else 0
        eth_dominance = (eth_market_cap / total_market_cap) * 100 if total_market_cap > 0 else 0
        
        # For Fear & Greed Index we would need a specific API
        # Here we just use a placeholder value
        fear_greed_index = 65  # Example value
        
        result = {
            "total_market_cap": total_market_cap,
            "total_volume_24h": total_volume,
            "btc_dominance": btc_dominance,
            "eth_dominance": eth_dominance,
            "fear_greed_index": fear_greed_index,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Cache the result in Redis for 60 seconds
        if redis_client:
            redis_client.setex(cache_key, 60, json.dumps(result))
            
        return result
    except Exception as e:
        logger.error(f"Error fetching market indicators: {e}")
        return {
            "total_market_cap": 0,
            "total_volume_24h": 0,
            "btc_dominance": 0,
            "eth_dominance": 0,
            "fear_greed_index": 0,
            "last_updated": datetime.utcnow().isoformat()
        }

async def get_candlestick_data(symbol: str, interval: str):
    """Fetch candlestick data for a specific crypto and timeframe"""
    try:
        # Check if data is in Redis cache
        cache_key = f"candles:{symbol}:{interval}"
        cached_data = redis_client.get(cache_key) if redis_client else None
        
        if cached_data:
            return json.loads(cached_data)
        
        # Get candlestick data from Binance
        candles = binance_client.get_klines(symbol=symbol, interval=interval, limit=100)
        
        formatted_candles = []
        for candle in candles:
            formatted_candles.append({
                "time": candle[0] / 1000,  # Convert milliseconds to seconds
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            })
        
        result = {
            "symbol": symbol,
            "interval": interval,
            "candles": formatted_candles,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Cache the result in Redis
        # Cache time depends on interval
        cache_time = 60  # Default 60 seconds
        if interval == '1m':
            cache_time = 30
        elif interval in ['5m', '15m']:
            cache_time = 120
        elif interval in ['1h', '4h']:
            cache_time = 300
        elif interval in ['1d', '1w']:
            cache_time = 3600
            
        if redis_client:
            redis_client.setex(cache_key, cache_time, json.dumps(result))
            
        return result
    except Exception as e:
        logger.error(f"Error fetching candlestick data: {e}")
        return {"symbol": symbol, "interval": interval, "candles": [], "last_updated": datetime.utcnow().isoformat()}

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Cryptocurrency Dashboard API"}

@api_router.get("/cryptocurrencies", response_model=List[Dict[str, Any]])
async def get_cryptocurrencies(symbols: Optional[str] = Query(None)):
    symbol_list = symbols.split(",") if symbols else None
    return await get_crypto_prices(symbol_list)

@api_router.get("/market-indicators")
async def get_market_indicators_api():
    return await get_market_indicators()

@api_router.get("/chart/{symbol}")
async def get_chart_data(symbol: str, interval: str = "1h"):
    return await get_candlestick_data(symbol, interval)

# WebSocket endpoint for real-time updates
@app.websocket("/ws/crypto-prices")
async def websocket_crypto_prices(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Initial data
        crypto_data = await get_crypto_prices()
        await websocket.send_text(json.dumps({
            "type": "crypto_prices",
            "data": crypto_data
        }))
        
        # Continuously send updates
        while True:
            await asyncio.sleep(5)  # Update every 5 seconds
            crypto_data = await get_crypto_prices()
            await websocket.send_text(json.dumps({
                "type": "crypto_prices",
                "data": crypto_data
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws/market-indicators")
async def websocket_market_indicators(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Initial data
        indicators = await get_market_indicators()
        await websocket.send_text(json.dumps({
            "type": "market_indicators",
            "data": indicators
        }))
        
        # Continuously send updates
        while True:
            await asyncio.sleep(15)  # Update every 15 seconds
            indicators = await get_market_indicators()
            await websocket.send_text(json.dumps({
                "type": "market_indicators",
                "data": indicators
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
