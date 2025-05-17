import os
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
def get_mongo_client():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url)
    return client

def get_async_mongo_client():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    return client

def get_database():
    client = get_mongo_client()
    return client.crypto_dashboard

def get_async_database():
    client = get_async_mongo_client()
    return client.crypto_dashboard
