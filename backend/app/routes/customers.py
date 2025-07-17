# backend/app/routes/customers.py
"""Customers API Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_active_user
from app.database import get_db

router = APIRouter()


@router.get("/")
async def get_customers(db: Session = Depends(get_db)):
    return {"message": "Customers endpoint"}
