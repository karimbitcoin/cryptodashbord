from fastapi import APIRouter

from app.api.endpoints import auth, crypto, user, news

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(crypto.router, prefix="/crypto", tags=["crypto"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
