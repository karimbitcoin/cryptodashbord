from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security settings
SECRET_KEY = os.environ.get("SECRET_KEY", "thisisasecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Functions
def verify_password(plain_password, hashed_password):
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Create a JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db=None):
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Mock user for development
    if user_id == "mock-user-id":
        return {
            "id": "mock-user-id",
            "email": "user@example.com",
            "username": "testuser"
        }
    
    # In a real app, we would look up the user in the database
    # user = await db.users.find_one({"_id": user_id})
    # if user is None:
    #     raise credentials_exception
    # return user
    
    # For now, we'll just return the user_id as a mock user
    return {
        "id": user_id,
        "email": "user@example.com",
        "username": f"user_{user_id[:8]}"
    }

def authenticate_user(email: str, password: str, db=None):
    """Authenticate a user"""
    # For development, we'll use a mock user
    if email == "user@example.com" and password == "password":
        return {
            "id": "mock-user-id",
            "email": "user@example.com",
            "username": "testuser"
        }
    
    # In a real app, we would look up the user in the database
    # user = await db.users.find_one({"email": email})
    # if not user or not verify_password(password, user["password"]):
    #     return None
    # return user
    
    # For now, just return None for any other credentials
    return None

async def get_user_by_email(email: str, db=None):
    """Get a user by email"""
    # For development, we'll use a mock user
    if email == "user@example.com":
        return {
            "id": "mock-user-id",
            "email": "user@example.com",
            "username": "testuser",
            "password": get_password_hash("password")  # Hashed password
        }
    
    # In a real app, we would look up the user in the database
    # return await db.users.find_one({"email": email})
    
    # For now, just return None for any other email
    return None

async def create_user(user_data, db=None):
    """Create a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email, db)
    if existing_user:
        return None
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user object
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    # In a real app, we would insert the user into the database
    # await db.users.insert_one(new_user)
    
    # For now, just return the user without the password
    return {
        "id": new_user["id"],
        "email": new_user["email"],
        "username": new_user["username"]
    }
