from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.coindesk_service import get_news_articles

router = APIRouter()

class NewsArticle(BaseModel):
    title: str
    url: str
    published_at: str
    source: str
    category: Optional[str] = None
    thumbnail: Optional[str] = None
    summary: Optional[str] = None

@router.get("/news", response_model=List[NewsArticle])
async def get_news(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get cryptocurrency news from CoinDesk
    """
    try:
        return get_news_articles(limit, category, search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
