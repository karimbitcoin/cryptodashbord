from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os
import asyncio
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path
import json
from binance.client import Client
import websockets
import requests
import pandas as pd

# Import our modules
import os
import sys
# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from auth import authenticate_user, create_access_token, get_current_user, create_user
from models import (UserCreate, UserLogin, UserResponse, Token, 
                   Portfolio, PortfolioCreate, PortfolioSummary, 
                   UserPreferences, CryptoCurrency, MarketIndicator, ChartData)

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
using_mock_data = True

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    binance_client.get_system_status()  # A simpler API call to check connection
    logger.info("Binance API connected successfully")
    using_mock_data = False
except Exception as e:
    logger.warning(f"Failed to connect to Binance API: {e}")
    logger.warning("Using mock data instead")
    using_mock_data = True

# Create the main app
app = FastAPI()

# Create routers with prefixes
api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth")
portfolio_router = APIRouter(prefix="/portfolio")
preferences_router = APIRouter(prefix="/preferences")

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

class NewsArticle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: str
    thumbnail: Optional[str] = None
    category: Optional[str] = None
    published_at: datetime = Field(default_factory=datetime.utcnow)

# Mock data for cryptocurrencies
def get_mock_crypto_data():
    """Generate mock cryptocurrency data"""
    mock_data = [
        {
            "symbol": "BTCUSDT",
            "price": 53495.23 + random.uniform(-500, 500),
            "price_change_24h": 1250.45 + random.uniform(-100, 100),
            "price_change_percentage_24h": 2.36 + random.uniform(-0.5, 0.5),
            "volume_24h": 24576000000 + random.uniform(-1000000000, 1000000000),
            "market_cap": 1034000000000 + random.uniform(-10000000000, 10000000000),
        },
        {
            "symbol": "ETHUSDT",
            "price": 2853.12 + random.uniform(-30, 30),
            "price_change_24h": 87.32 + random.uniform(-10, 10),
            "price_change_percentage_24h": 3.15 + random.uniform(-0.5, 0.5),
            "volume_24h": 14325000000 + random.uniform(-500000000, 500000000),
            "market_cap": 345000000000 + random.uniform(-5000000000, 5000000000),
        },
        {
            "symbol": "BNBUSDT",
            "price": 567.89 + random.uniform(-5, 5),
            "price_change_24h": 14.56 + random.uniform(-2, 2),
            "price_change_percentage_24h": 2.63 + random.uniform(-0.5, 0.5),
            "volume_24h": 2145000000 + random.uniform(-100000000, 100000000),
            "market_cap": 78900000000 + random.uniform(-1000000000, 1000000000),
        },
        {
            "symbol": "SOLUSDT",
            "price": 124.34 + random.uniform(-3, 3),
            "price_change_24h": 8.76 + random.uniform(-1, 1),
            "price_change_percentage_24h": 7.58 + random.uniform(-0.5, 0.5),
            "volume_24h": 4567000000 + random.uniform(-100000000, 100000000),
            "market_cap": 56700000000 + random.uniform(-1000000000, 1000000000),
        },
        {
            "symbol": "ADAUSDT",
            "price": 0.58 + random.uniform(-0.01, 0.01),
            "price_change_24h": 0.03 + random.uniform(-0.005, 0.005),
            "price_change_percentage_24h": 5.45 + random.uniform(-0.5, 0.5),
            "volume_24h": 1234000000 + random.uniform(-50000000, 50000000),
            "market_cap": 23400000000 + random.uniform(-500000000, 500000000),
        },
        {
            "symbol": "XRPUSDT",
            "price": 0.52 + random.uniform(-0.01, 0.01),
            "price_change_24h": -0.03 + random.uniform(-0.005, 0.005),
            "price_change_percentage_24h": -5.45 + random.uniform(-0.5, 0.5),
            "volume_24h": 2345000000 + random.uniform(-50000000, 50000000),
            "market_cap": 27600000000 + random.uniform(-500000000, 500000000),
        },
        {
            "symbol": "DOGEUSDT",
            "price": 0.132 + random.uniform(-0.005, 0.005),
            "price_change_24h": 0.007 + random.uniform(-0.001, 0.001),
            "price_change_percentage_24h": 5.61 + random.uniform(-0.5, 0.5),
            "volume_24h": 1987000000 + random.uniform(-50000000, 50000000),
            "market_cap": 18700000000 + random.uniform(-300000000, 300000000),
        },
        {
            "symbol": "DOTUSDT",
            "price": 8.43 + random.uniform(-0.1, 0.1),
            "price_change_24h": -0.25 + random.uniform(-0.05, 0.05),
            "price_change_percentage_24h": -2.88 + random.uniform(-0.5, 0.5),
            "volume_24h": 654000000 + random.uniform(-20000000, 20000000),
            "market_cap": 10500000000 + random.uniform(-200000000, 200000000),
        }
    ]
    
    # Add last_updated field to each item
    for item in mock_data:
        item["last_updated"] = datetime.utcnow().isoformat()
        
    return mock_data

# Mock data for market indicators
def get_mock_market_indicators():
    """Generate mock market indicators data"""
    return {
        "total_market_cap": 2345000000000 + random.uniform(-20000000000, 20000000000),
        "total_volume_24h": 98700000000 + random.uniform(-2000000000, 2000000000),
        "btc_dominance": 43.5 + random.uniform(-0.3, 0.3),
        "eth_dominance": 18.2 + random.uniform(-0.2, 0.2),
        "fear_greed_index": 65 + random.randint(-5, 5),
        "last_updated": datetime.utcnow().isoformat()
    }

# Mock data for news
def get_mock_news(limit: int = 10, category: Optional[str] = None, search: Optional[str] = None):
    """Generate mock news data with optional filtering"""
    mock_news = [
        {
            "title": "Bitcoin Surges Past $50,000 as Institutional Interest Grows",
            "summary": "Bitcoin's price reaches new heights as more institutions adopt cryptocurrency.",
            "content": "The world's largest cryptocurrency has seen significant growth...",
            "url": "https://example.com/news/1",
            "source": "CryptoNews",
            "thumbnail": "https://example.com/images/bitcoin.jpg",
            "category": "market",
            "published_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
        },
        {
            "title": "Ethereum 2.0 Upgrade Shows Promise in Latest Tests",
            "summary": "The long-awaited Ethereum upgrade demonstrates improved performance.",
            "content": "Recent testing of the Ethereum 2.0 network has shown promising results...",
            "url": "https://example.com/news/2",
            "source": "BlockchainDaily",
            "thumbnail": "https://example.com/images/ethereum.jpg",
            "category": "technology",
            "published_at": (datetime.utcnow() - timedelta(hours=4)).isoformat()
        },
        {
            "title": "New Cryptocurrency Regulations Proposed in EU",
            "summary": "European Union considers new framework for crypto assets.",
            "content": "The European Commission has unveiled new regulatory proposals...",
            "url": "https://example.com/news/3",
            "source": "CryptoRegulation",
            "thumbnail": "https://example.com/images/eu-flag.jpg",
            "category": "regulation",
            "published_at": (datetime.utcnow() - timedelta(hours=6)).isoformat()
        },
        {
            "title": "DeFi Protocol Reports Record Trading Volume",
            "summary": "Decentralized finance continues to grow with latest milestone.",
            "content": "A leading DeFi protocol has reported unprecedented trading volumes...",
            "url": "https://example.com/news/4",
            "source": "DeFiNews",
            "thumbnail": "https://example.com/images/defi.jpg",
            "category": "defi",
            "published_at": (datetime.utcnow() - timedelta(hours=8)).isoformat()
        },
        {
            "title": "Major Bank Launches Cryptocurrency Custody Service",
            "summary": "Traditional financial institution enters the crypto space.",
            "content": "One of the world's largest banks has announced a new crypto custody solution...",
            "url": "https://example.com/news/5",
            "source": "BankingNews",
            "thumbnail": "https://example.com/images/bank.jpg",
            "category": "adoption",
            "published_at": (datetime.utcnow() - timedelta(hours=10)).isoformat()
        }
    ]
    
    # Filter by category if specified
    if category:
        mock_news = [news for news in mock_news if news["category"] == category]
    
    # Filter by search term if specified
    if search:
        search = search.lower()
        mock_news = [
            news for news in mock_news 
            if search in news["title"].lower() or 
               search in news["summary"].lower() or 
               search in news["content"].lower()
        ]
    
    # Limit the number of results
    mock_news = mock_news[:limit]
    
    return mock_news

# Mock data for candlestick charts
def get_mock_candlestick_data(symbol, interval):
    """Generate mock candlestick data"""
    # Base values that differ by symbol
    base_values = {
        "BTCUSDT": {"price": 53000, "volatility": 1500},
        "ETHUSDT": {"price": 2800, "volatility": 100},
        "BNBUSDT": {"price": 560, "volatility": 20},
        "SOLUSDT": {"price": 120, "volatility": 10},
        "ADAUSDT": {"price": 0.58, "volatility": 0.05},
        "XRPUSDT": {"price": 0.52, "volatility": 0.04},
        "DOGEUSDT": {"price": 0.13, "volatility": 0.01},
        "DOTUSDT": {"price": 8.5, "volatility": 0.5},
    }
    
    # Default values if symbol not found
    base_price = base_values.get(symbol, {"price": 100, "volatility": 5})["price"]
    volatility = base_values.get(symbol, {"price": 100, "volatility": 5})["volatility"]
    
    # Generate 100 candlesticks
    candles = []
    now = datetime.utcnow().timestamp()
    
    # Determine time interval in seconds
    interval_seconds = 3600  # Default 1h
    if interval == '1m':
        interval_seconds = 60
    elif interval == '5m':
        interval_seconds = 300
    elif interval == '15m':
        interval_seconds = 900
    elif interval == '4h':
        interval_seconds = 14400
    elif interval == '1d':
        interval_seconds = 86400
    elif interval == '1w':
        interval_seconds = 604800
    
    price = base_price
    for i in range(100):
        time = now - (99 - i) * interval_seconds
        
        # Create some price movement
        change = (volatility * 0.2) * (0.5 - random.random())
        price += change
        
        open_price = price
        close_price = price + (volatility * 0.1) * (0.5 - random.random())
        high_price = max(open_price, close_price) + (volatility * 0.05) * random.random()
        low_price = min(open_price, close_price) - (volatility * 0.05) * random.random()
        volume = base_price * 1000 * (0.5 + random.random())
        
        candles.append({
            "time": time,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })
    
    return {
        "symbol": symbol,
        "interval": interval,
        "candles": candles,
        "last_updated": datetime.utcnow().isoformat()
    }

# Helper Functions
async def get_crypto_prices(symbols: List[str] = None):
    """Fetch current prices for cryptocurrencies from Binance API or mock data"""
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "DOTUSDT"]
    
    if using_mock_data:
        mock_data = get_mock_crypto_data()
        # Filter the mock data based on the requested symbols
        if symbols:
            mock_data = [crypto for crypto in mock_data if crypto["symbol"] in symbols]
        return mock_data
        
    # If we're not using mock data, fetch from Binance API
    result = []
    try:
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
                
        return result
    except Exception as e:
        logger.error(f"Error fetching crypto prices from Binance: {e}")
        # Fall back to mock data if there's an error with Binance API
        return get_mock_crypto_data()

async def get_market_indicators():
    """Fetch overall market indicators"""
    if using_mock_data:
        return get_mock_market_indicators()
        
    try:
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
            
        return result
    except Exception as e:
        logger.error(f"Error fetching market indicators from Binance: {e}")
        # Fall back to mock data if there's an error with Binance API
        return get_mock_market_indicators()

async def get_candlestick_data(symbol: str, interval: str):
    """Fetch candlestick data for a specific crypto and timeframe"""
    if using_mock_data:
        return get_mock_candlestick_data(symbol, interval)
        
    try:
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
            
        return result
    except Exception as e:
        logger.error(f"Error fetching candlestick data from Binance: {e}")
        # Fall back to mock data if there's an error with Binance API
        return get_mock_candlestick_data(symbol, interval)

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

@api_router.get("/news")
async def get_news_api(limit: int = 10, category: Optional[str] = None, search: Optional[str] = None):
    """Get news articles with optional filtering by category and search term"""
    return get_mock_news(limit, category, search)

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

# Authentication routes
@auth_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    user = await create_user(user_data, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    return user

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get the current user's information"""
    return current_user

# Portfolio routes
@portfolio_router.post("", response_model=Portfolio)
async def create_portfolio(portfolio_data: PortfolioCreate, current_user: dict = Depends(get_current_user)):
    """Create a new portfolio"""
    new_portfolio = Portfolio(
        id=str(uuid.uuid4()),
        user_id=current_user["id"],
        name=portfolio_data.name,
        assets=portfolio_data.assets
    )
    
    # In a real app, we would insert the portfolio into the database
    # await db.portfolios.insert_one(new_portfolio.dict())
    
    return new_portfolio

@portfolio_router.get("", response_model=List[PortfolioSummary])
async def get_portfolios(current_user: dict = Depends(get_current_user)):
    """Get all portfolios for the current user"""
    # In a real app, we would fetch portfolios from the database
    # portfolios = await db.portfolios.find({"user_id": current_user["id"]}).to_list(length=None)
    
    # For now, return a mock portfolio
    mock_portfolio = PortfolioSummary(
        id="mock-portfolio-id",
        name="My Crypto Portfolio",
        total_value=15783.45,
        total_profit_loss=2341.23,
        profit_loss_percentage=17.42,
        assets_count=5,
        updated_at=datetime.utcnow()
    )
    
    return [mock_portfolio]

@portfolio_router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(portfolio_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific portfolio"""
    # In a real app, we would fetch the portfolio from the database
    # portfolio = await db.portfolios.find_one({"_id": portfolio_id, "user_id": current_user["id"]})
    # if not portfolio:
    #     raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # For now, return a mock portfolio
    from models import PortfolioAsset
    mock_assets = [
        PortfolioAsset(
            symbol="BTCUSDT",
            amount=0.12,
            purchase_price=48500.00,
            purchase_date=datetime.utcnow() - timedelta(days=30)
        ),
        PortfolioAsset(
            symbol="ETHUSDT",
            amount=1.5,
            purchase_price=2650.00,
            purchase_date=datetime.utcnow() - timedelta(days=15)
        ),
        PortfolioAsset(
            symbol="BNBUSDT",
            amount=5.0,
            purchase_price=552.00,
            purchase_date=datetime.utcnow() - timedelta(days=7)
        ),
        PortfolioAsset(
            symbol="SOLUSDT",
            amount=20.0,
            purchase_price=115.00,
            purchase_date=datetime.utcnow() - timedelta(days=10)
        ),
        PortfolioAsset(
            symbol="ADAUSDT",
            amount=1000.0,
            purchase_price=0.55,
            purchase_date=datetime.utcnow() - timedelta(days=20)
        )
    ]
    
    mock_portfolio = Portfolio(
        id=portfolio_id,
        user_id=current_user["id"],
        name="My Crypto Portfolio",
        assets=mock_assets,
        created_at=datetime.utcnow() - timedelta(days=45),
        updated_at=datetime.utcnow()
    )
    
    return mock_portfolio

@portfolio_router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a portfolio"""
    # In a real app, we would delete the portfolio from the database
    # result = await db.portfolios.delete_one({"_id": portfolio_id, "user_id": current_user["id"]})
    # if result.deleted_count == 0:
    #     raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return {"message": "Portfolio deleted successfully"}

# User preferences routes
@preferences_router.get("", response_model=UserPreferences)
async def get_preferences(current_user: dict = Depends(get_current_user)):
    """Get user preferences"""
    # In a real app, we would fetch preferences from the database
    # preferences = await db.preferences.find_one({"user_id": current_user["id"]})
    # if not preferences:
    #     # Create default preferences
    #     preferences = UserPreferences(user_id=current_user["id"])
    #     await db.preferences.insert_one(preferences.dict())
    
    # For now, return mock preferences
    mock_preferences = UserPreferences(
        id="mock-preferences-id",
        user_id=current_user["id"],
        default_currency="USD",
        dark_mode=True,
        favorite_coins=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        dashboard_layout={
            "portfolio": {"x": 0, "y": 0, "w": 1, "h": 1},
            "chart": {"x": 1, "y": 0, "w": 2, "h": 2},
            "market": {"x": 0, "y": 1, "w": 1, "h": 1}
        }
    )
    
    return mock_preferences

@preferences_router.put("", response_model=UserPreferences)
async def update_preferences(preferences_data: dict, current_user: dict = Depends(get_current_user)):
    """Update user preferences"""
    # In a real app, we would update preferences in the database
    # await db.preferences.update_one(
    #     {"user_id": current_user["id"]},
    #     {"$set": {**preferences_data, "updated_at": datetime.utcnow()}}
    # )
    
    # For now, return mock updated preferences
    mock_preferences = UserPreferences(
        id="mock-preferences-id",
        user_id=current_user["id"],
        **preferences_data,
        updated_at=datetime.utcnow()
    )
    
    return mock_preferences

# Include all routers in the main app
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(portfolio_router, prefix="/portfolio")
api_router.include_router(preferences_router, prefix="/preferences")
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
