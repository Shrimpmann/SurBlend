# backend/app/routes/blends.py
"""Blends API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_active_user
from app.database import get_db

router = APIRouter()


@router.get("/")
async def get_blends(db: Session = Depends(get_db)):
    return {"message": "Blends endpoint"}
