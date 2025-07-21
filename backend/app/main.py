"""
SurBlend - Fertilizer Blending & Quoting System
Main FastAPI Application
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.services.startup import initialize_database
from app.routes import analytics, blends, customers, ingredients, quotes, system, users
from dotenv import load_dotenv
import psutil
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define lifespan function before app instantiation
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting SurBlend application...")
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
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "SurBlend API", "version": "1.0.0", "status": "operational"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint"""
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

# Include routers
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["ingredients"])
app.include_router(blends.router, prefix="/api/blends", tags=["blends"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["quotes"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
