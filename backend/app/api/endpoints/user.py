from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.models import UserPreferences, Portfolio, PortfolioCreate, PortfolioSummary
from app.core.auth import get_current_user
from app.db.database import get_database

router = APIRouter()

@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """
    Get user preferences like favorite coins, dashboard layout, display settings
    """
    db = get_database()
    prefs = db.user_preferences.find_one({"username": current_user["username"]})
    
    if not prefs:
        # Create default preferences if none exist
        default_prefs = {
            "username": current_user["username"],
            "favorite_coins": ["BTC", "ETH", "SOL", "BNB", "ADA"],
            "dashboard_layout": "default",
            "theme": "dark",
            "default_currency": "USD"
        }
        db.user_preferences.insert_one(default_prefs)
        return default_prefs
    
    return prefs

@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update user preferences
    """
    db = get_database()
    
    # Ensure the username matches the authenticated user
    if preferences.username != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify another user's preferences"
        )
    
    # Update preferences in the database
    result = db.user_preferences.update_one(
        {"username": current_user["username"]},
        {"$set": preferences.dict()},
        upsert=True
    )
    
    return preferences

@router.get("/portfolio", response_model=List[Portfolio])
async def get_user_portfolio(current_user: dict = Depends(get_current_user)):
    """
    Get user's cryptocurrency portfolio
    """
    db = get_database()
    portfolio = list(db.portfolios.find({"username": current_user["username"]}))
    
    return portfolio or []

@router.post("/portfolio", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
async def add_portfolio_entry(
    entry: PortfolioCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new entry to the portfolio
    """
    db = get_database()
    
    # Create portfolio entry with the authenticated username
    portfolio_entry = {
        "username": current_user["username"],
        "symbol": entry.symbol,
        "amount": entry.amount,
        "purchase_price": entry.purchase_price,
        "purchase_date": entry.purchase_date,
        "notes": entry.notes
    }
    
    result = db.portfolios.insert_one(portfolio_entry)
    portfolio_entry["_id"] = str(result.inserted_id)
    
    return portfolio_entry

@router.delete("/portfolio/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a portfolio entry
    """
    db = get_database()
    
    # Ensure the entry belongs to the authenticated user
    entry = db.portfolios.find_one({"_id": entry_id, "username": current_user["username"]})
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio entry not found"
        )
    
    db.portfolios.delete_one({"_id": entry_id})
    
    return None

@router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(current_user: dict = Depends(get_current_user)):
    """
    Get summary of user's portfolio with current values
    """
    db = get_database()
    portfolio = list(db.portfolios.find({"username": current_user["username"]}))
    
    if not portfolio:
        return {
            "total_value": 0,
            "total_investment": 0,
            "profit_loss": 0,
            "profit_loss_percentage": 0
        }
    
    # In a real implementation, we'd get current prices from the API
    # For now, we'll use the purchase price as current price (no profit/loss)
    total_investment = sum(entry["amount"] * entry["purchase_price"] for entry in portfolio)
    total_value = total_investment  # In a real implementation, this would use current prices
    
    return {
        "total_value": total_value,
        "total_investment": total_investment,
        "profit_loss": 0,
        "profit_loss_percentage": 0
    }
