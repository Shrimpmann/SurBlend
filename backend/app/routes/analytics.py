# backend/app/routes/analytics.py
"""Analytics API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_active_user
from app.database import get_db

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    return {"message": "Analytics endpoint"}
