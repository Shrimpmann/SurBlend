
from sqlalchemy.orm import Session
from app.models import Ingredient  # Adjust if model is elsewhere
from app.schemas import schemas  # Adjust based on your schemas.py

def get_ingredients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Ingredient).offset(skip).limit(limit).all()

def get_ingredient_by_id(db: Session, ingredient_id: int):
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

def create_ingredient(db: Session, ingredient: schemas.IngredientCreate):
    db_ingredient = Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient
