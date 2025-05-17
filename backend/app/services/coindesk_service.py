import os
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# CoinDesk API key and URL
COINDESK_API_KEY = os.environ.get("COINDESK_API_KEY", "a1767cfd2957079cad70abd9850f473d0d033e55851bfe550c15b74bd83d8eaf")
COINDESK_API_URL = "https://data.cryptocompare.com/v2/news"

# Mock news articles for when the API is unavailable
MOCK_NEWS_ARTICLES = [
    {
        "title": "Bitcoin Surges Past $60,000 As ETF Hype Continues",
        "url": "https://example.com/bitcoin-etf-hype",
        "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "source": "CryptoNews",
        "category": "Bitcoin",
        "thumbnail": "https://example.com/images/bitcoin-etf.jpg",
        "summary": "Bitcoin has surged past $60,000 as excitement builds around potential ETF approvals."
    },
    {
        "title": "Ethereum Upgrade Targets September for Major Protocol Changes",
        "url": "https://example.com/ethereum-upgrade",
        "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
        "source": "BlockchainInsider",
        "category": "Ethereum",
        "thumbnail": "https://example.com/images/ethereum-upgrade.jpg",
        "summary": "The Ethereum community has set a target date in September for the next major protocol upgrade."
    },
    {
        "title": "Solana DeFi Ecosystem Sees Record Growth in Q2",
        "url": "https://example.com/solana-defi-growth",
        "published_at": (datetime.now() - timedelta(hours=8)).isoformat(),
        "source": "DeFiPulse",
        "category": "DeFi",
        "thumbnail": "https://example.com/images/solana-defi.jpg",
        "summary": "Solana's DeFi ecosystem has seen unprecedented growth in Q2, with TVL reaching new all-time highs."
    },
    {
        "title": "SEC Chair Comments on Regulatory Framework for Cryptocurrencies",
        "url": "https://example.com/sec-crypto-regulation",
        "published_at": (datetime.now() - timedelta(hours=10)).isoformat(),
        "source": "RegulatoryWatch",
        "category": "Regulation",
        "thumbnail": "https://example.com/images/sec-regulation.jpg",
        "summary": "The SEC Chair has provided new insights into the agency's approach to cryptocurrency regulation."
    },
    {
        "title": "New Stablecoin Project Backed by Major Banks Announces Launch",
        "url": "https://example.com/bank-stablecoin-launch",
        "published_at": (datetime.now() - timedelta(hours=12)).isoformat(),
        "source": "CoinTelegraph",
        "category": "Stablecoins",
        "thumbnail": "https://example.com/images/stablecoin-launch.jpg",
        "summary": "A consortium of major banks has announced the launch of a new regulated stablecoin project."
    },
    {
        "title": "NFT Market Shows Signs of Recovery After Months of Decline",
        "url": "https://example.com/nft-market-recovery",
        "published_at": (datetime.now() - timedelta(hours=15)).isoformat(),
        "source": "NFTDaily",
        "category": "NFTs",
        "thumbnail": "https://example.com/images/nft-recovery.jpg",
        "summary": "The NFT market is showing signs of recovery after months of declining sales volumes."
    },
    {
        "title": "Central Bank Digital Currencies: New Report Analyzes Global Progress",
        "url": "https://example.com/cbdc-global-progress",
        "published_at": (datetime.now() - timedelta(hours=18)).isoformat(),
        "source": "CentralBankNews",
        "category": "CBDCs",
        "thumbnail": "https://example.com/images/cbdc-progress.jpg",
        "summary": "A new report provides a comprehensive analysis of CBDC development efforts around the world."
    },
    {
        "title": "Major Exchange Announces New Listing and Trading Pairs",
        "url": "https://example.com/exchange-new-listings",
        "published_at": (datetime.now() - timedelta(hours=20)).isoformat(),
        "source": "CryptoExchangeNews",
        "category": "Exchanges",
        "thumbnail": "https://example.com/images/exchange-listings.jpg",
        "summary": "A major cryptocurrency exchange has announced new token listings and trading pairs."
    },
    {
        "title": "Layer-2 Solutions See Surge in Adoption as Ethereum Fees Rise",
        "url": "https://example.com/layer2-adoption-surge",
        "published_at": (datetime.now() - timedelta(hours=22)).isoformat(),
        "source": "Layer2Report",
        "category": "Scaling",
        "thumbnail": "https://example.com/images/layer2-adoption.jpg",
        "summary": "Layer-2 scaling solutions are seeing a surge in adoption as Ethereum gas fees rise again."
    },
    {
        "title": "New Crypto Tax Guidance Released: What Investors Need to Know",
        "url": "https://example.com/crypto-tax-guidance",
        "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "source": "CryptoTaxNews",
        "category": "Taxes",
        "thumbnail": "https://example.com/images/crypto-taxes.jpg",
        "summary": "New tax guidance has been released for cryptocurrency investors. Here's what you need to know."
    }
]

def get_news_articles(
    limit: int = 10,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get cryptocurrency news articles from CoinDesk API
    
    Args:
        limit: Maximum number of articles to return
        category: Filter by category (e.g., "Bitcoin", "Ethereum")
        search: Search term to filter articles
        
    Returns:
        List of news articles
    """
    # Check if api key is available
    if not COINDESK_API_KEY:
        logger.warning("CoinDesk API key not found, using mock data")
        return MOCK_NEWS_ARTICLES[:limit]
    
    try:
        # Prepare params
        params = {
            "api_key": COINDESK_API_KEY,
            "sortOrder": "latest",
            "limit": limit
        }
        
        # Add filters if provided
        if category:
            params["categories"] = category
        if search:
            params["q"] = search
        
        # Make API call
        response = requests.get(COINDESK_API_URL, params=params)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            articles = data.get("Data", [])
            
            # Format the response to match our model
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("published_on", ""),
                    "source": article.get("source", ""),
                    "category": article.get("categories", ""),
                    "thumbnail": article.get("imageurl", ""),
                    "summary": article.get("body", "")[:200] + "..." if article.get("body") else ""
                })
                
            return formatted_articles
        else:
            logger.error(f"CoinDesk API error: {response.status_code} - {response.text}")
            return MOCK_NEWS_ARTICLES[:limit]
            
    except Exception as e:
        logger.error(f"Error calling CoinDesk API: {e}")
        return MOCK_NEWS_ARTICLES[:limit]
