#!/usr/bin/env python3
"""
SurBlend - Fertilizer Blending & Quoting System
Main FastAPI Application
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
from app.services.startup import initialize_database
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from app.auth.security import create_access_token, get_password_hash, verify_password

# Import our modules (to be created)
from app.database import Base, engine, get_db
from app.models import User
from app.routes import analytics, blends, customers, ingredients, quotes, system, users
from app.schemas.schemas import Token, TokenData
from app.services.startup import create_default_admin, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting SurBlend application...")

    # Initialize database
    await initialize_database()

    yield

    logger.info("Shutting down SurBlend application...")


# Create FastAPI app
app = FastAPI(
    title="SurBlend API",
    description="Fertilizer Blending & Quoting System",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        f"http://{os.getenv('HOST_IP', 'localhost')}:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "SurBlend API", "version": "1.0.0", "status": "operational"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    import psutil

    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / 1024 / 1024,
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / 1024 / 1024 / 1024,
        },
    }


# Authentication endpoint
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """Login endpoint for OAuth2 password flow"""
    from sqlalchemy.orm import Session

    from app.crud.users import get_user_by_username

    user = get_user_by_username(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    # Create access token
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")))
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


# Include routers
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["ingredients"])
app.include_router(blends.router, prefix="/api/blends", tags=["blends"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["quotes"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

if __name__ == "__main__":
    # For development only
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
