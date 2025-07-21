from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Blend, Ingredient, Chemical
from app.schemas import BlendCreate, BlendResponse
from typing import List

router = APIRouter(prefix="/api/blends", tags=["blends"])

@router.get("/", response_model=List[BlendResponse])
def get_blends(db: Session = Depends(get_db)):
    blends = db.query(Blend).all()
    return blends

@router.post("/", response_model=BlendResponse)
def create_blend(blend: BlendCreate, db: Session = Depends(get_db)):
    db_blend = Blend(
        name=blend.name,
        total_cost=blend.totalCost,
        application_rate=blend.applicationRate,
        target_n=blend.nutrients.get('n'),
        target_p=blend.nutrients.get('p'),
        target_k=blend.nutrients.get('k'),
        target_s=blend.nutrients.get('s'),
        target_ca=blend.nutrients.get('ca'),
        target_mg=blend.nutrients.get('mg'),
        target_fe=blend.nutrients.get('fe'),
        target_zn=blend.nutrients.get('zn'),
        target_mn=blend.nutrients.get('mn'),
        target_b=blend.nutrients.get('b'),
        target_cl=blend.nutrients.get('cl')
    )
    db.add(db_blend)
    db.commit()
    db.refresh(db_blend)
    # Add ingredients to blend_ingredients
    for ing in blend.ingredients:
        db_ingredient = db.query(Ingredient).filter(Ingredient.id == ing.ingredientId).first()
        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        db.execute(
            blend_ingredients.insert().values(
                blend_id=db_blend.id,
                ingredient_id=ing.ingredientId,
                percentage=ing.quantity / blend.applicationRate * 100,
                amount=ing.quantity
            )
        )
    # Add chemicals to blend_chemicals
    for chem in blend.chemicals:
        db_chemical = db.query(Chemical).filter(Chemical.id == chem.chemicalId).first()
        if not db_chemical:
            raise HTTPException(status_code=404, detail="Chemical not found")
        db.execute(
            blend_chemicals.insert().values(
                blend_id=db_blend.id,
                chemical_id=chem.chemicalId,
                ai_percentage=chem.aiPercentage,
                amount=chem.aiPercentage * blend.applicationRate / 100
            )
        )
    db.commit()
    return db_blend
