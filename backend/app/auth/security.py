"""
SurBlend Security Module
JWT authentication and password hashing
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
from functools import wraps
from app.database import get_db
from app.models import User, UserRole
from app.schemas.schemas import TokenData
from app.crud.users import get_user_by_username
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secure-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    # Convert UserRole enum to string if present
    if "role" in to_encode and isinstance(to_encode["role"], UserRole):
        to_encode["role"] = to_encode["role"].value
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    # Convert UserRole enum to string if present
    if "role" in to_encode and isinstance(to_encode["role"], UserRole):
        to_encode["role"] = to_encode["role"].value
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Ensure the current user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RoleChecker:
    """Dependency for checking user roles"""
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

# Common role dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_sales = RoleChecker([UserRole.ADMIN, UserRole.SALES_REP])
require_viewer = RoleChecker([UserRole.ADMIN, UserRole.SALES_REP, UserRole.VIEWER])

class RateLimiter:
    """Simple rate limiter for login attempts"""
    def __init__(self, calls: int = 20, period: int = 300):
        self.calls = calls
        self.period = period
        self.calls_made = defaultdict(list)

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request:
                client_ip = request.client.host
                now = time.time()
                # Clean old calls
                self.calls_made[client_ip] = [
                    call_time for call_time in self.calls_made[client_ip]
                    if call_time > now - self.period
                ]
                # Check rate limit
                if len(self.calls_made[client_ip]) >= self.calls:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests"
                    )
                # Record this call
                self.calls_made[client_ip].append(now)
            return await func(*args, **kwargs)
        return wrapper

# Create rate limiter for login endpoint
login_rate_limiter = RateLimiter(calls=20, period=300)  # 20 attempts per 5 minutes
