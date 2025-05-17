from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# User models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Cryptocurrency models
class CryptoCurrency(BaseModel):
    symbol: str
    price: float
    price_change_24h: float
    price_change_percentage_24h: float
    volume_24h: float
    market_cap: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Portfolio models
class PortfolioAsset(BaseModel):
    symbol: str
    amount: float
    purchase_price: float
    purchase_date: Optional[datetime] = None

class PortfolioCreate(BaseModel):
    assets: List[PortfolioAsset]
    name: str = "My Portfolio"

class Portfolio(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    assets: List[PortfolioAsset]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PortfolioSummary(BaseModel):
    id: str
    name: str
    total_value: float
    total_profit_loss: float
    profit_loss_percentage: float
    assets_count: int
    updated_at: datetime

# User preferences models
class UserPreferences(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    default_currency: str = "USD"
    dark_mode: bool = True
    favorite_coins: List[str] = []
    dashboard_layout: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Market indicator models
class MarketIndicator(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_market_cap: float
    total_volume_24h: float
    btc_dominance: float
    eth_dominance: float
    fear_greed_index: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Chart data model
class ChartData(BaseModel):
    symbol: str
    interval: str
    candles: List[Dict[str, Any]]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# News item model
class NewsItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    source: str
    url: str
    image_url: Optional[str] = None
    published_at: datetime
    categories: List[str] = []
    related_coins: List[str] = []
