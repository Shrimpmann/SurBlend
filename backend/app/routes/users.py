# backend/app/routes/users.py
"""Users API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import require_admin

router = APIRouter()

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    return current_user

