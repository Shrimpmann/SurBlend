from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Chemical
from app.schemas import ChemicalCreate, ChemicalResponse
from typing import List

router = APIRouter(prefix="/api/chemicals", tags=["chemicals"])

@router.get("/", response_model=List[ChemicalResponse])
def get_chemicals(db: Session = Depends(get_db)):
    chemicals = db.query(Chemical).all()
    return chemicals

@router.post("/", response_model=ChemicalResponse)
def create_chemical(chemical: ChemicalCreate, db: Session = Depends(get_db)):
    db_chemical = Chemical(**chemical.dict())
    db.add(db_chemical)
    db.commit()
    db.refresh(db_chemical)
    return db_chemical

@router.delete("/{id}")
def delete_chemical(id: int, db: Session = Depends(get_db)):
    db_chemical = db.query(Chemical).filter(Chemical.id == id).first()
    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    db.delete(db_chemical)
    db.commit()
    return {"message": "Chemical deleted"}
