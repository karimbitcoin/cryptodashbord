from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.models import CryptoCurrency, MarketIndicator, ChartData
from app.services.binance_service import get_crypto_data, get_market_indicators, get_chart_data
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/cryptocurrencies", response_model=List[CryptoCurrency])
async def get_cryptocurrencies(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of cryptocurrencies with current prices and 24h change
    """
    try:
        return get_crypto_data(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-indicators", response_model=List[MarketIndicator])
async def get_market_indicators(current_user: dict = Depends(get_current_user)):
    """
    Get market indicators like total market cap, trading volume, Bitcoin dominance
    """
    try:
        return get_market_indicators()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/{symbol}", response_model=ChartData)
async def get_crypto_chart(
    symbol: str,
    interval: str = Query("1d", regex="^(1m|5m|15m|30m|1h|2h|4h|6h|8h|12h|1d|3d|1w|1M)$"),
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get chart data for a specific cryptocurrency
    """
    if not start_time:
        start_time = datetime.now() - timedelta(days=30)
    if not end_time:
        end_time = datetime.now()
        
    try:
        return get_chart_data(symbol, interval, limit, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
