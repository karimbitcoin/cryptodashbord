import os
import json
import logging
from typing import Any, Optional, Callable
import redis
from functools import wraps
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    logger.warning("Caching will be disabled")
    REDIS_AVAILABLE = False

def cache_data(key_prefix: str, ttl_seconds: int = 300):
    """
    Decorator to cache function results in Redis
    
    Args:
        key_prefix: Prefix for Redis keys
        ttl_seconds: Time-to-live in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return func(*args, **kwargs)
            
            # Create a cache key from function args and kwargs
            cache_key = f"{key_prefix}:{func.__name__}:"
            
            # Add args to key
            if args:
                cache_key += ":".join(str(arg) for arg in args)
            
            # Add sorted kwargs to key
            if kwargs:
                kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key += ":" + kwargs_str
            
            # Try to get from cache
            cached_data = redis_client.get(cache_key)
            if cached_data:
                try:
                    return json.loads(cached_data)
                except Exception as e:
                    logger.error(f"Error decoding cached data: {e}")
            
            # If not in cache, call function
            result = func(*args, **kwargs)
            
            # Store result in cache
            try:
                redis_client.setex(
                    cache_key,
                    ttl_seconds,
                    json.dumps(result)
                )
            except Exception as e:
                logger.error(f"Error caching data: {e}")
            
            return result
        
        return wrapper
    
    return decorator

def get_cached_data(key: str) -> Optional[Any]:
    """
    Get data from Redis cache
    
    Args:
        key: Redis key
        
    Returns:
        Cached data or None
    """
    if not REDIS_AVAILABLE:
        return None
    
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.error(f"Error getting cached data: {e}")
        return None

def set_cached_data(key: str, data: Any, ttl_seconds: int = 300) -> bool:
    """
    Set data in Redis cache
    
    Args:
        key: Redis key
        data: Data to cache
        ttl_seconds: Time-to-live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        redis_client.setex(
            key,
            ttl_seconds,
            json.dumps(data)
        )
        return True
    except Exception as e:
        logger.error(f"Error setting cached data: {e}")
        return False

def delete_cached_data(key: str) -> bool:
    """
    Delete data from Redis cache
    
    Args:
        key: Redis key
        
    Returns:
        True if successful, False otherwise
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Error deleting cached data: {e}")
        return False

def clear_cache_by_prefix(prefix: str) -> bool:
    """
    Clear all keys matching a prefix
    
    Args:
        prefix: Key prefix
        
    Returns:
        True if successful, False otherwise
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        for key in redis_client.scan_iter(f"{prefix}*"):
            redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False
