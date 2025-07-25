# backend/app/routes/system.py
"""System API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import require_admin
from app.database import get_db

router = APIRouter()


@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    return {"message": "System settings endpoint"}
