# backend/app/routes/quotes.py
"""Quotes API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import get_current_active_user

router = APIRouter()

@router.get("/")
async def get_quotes(db: Session = Depends(get_db)):
    return {"message": "Quotes endpoint"}

