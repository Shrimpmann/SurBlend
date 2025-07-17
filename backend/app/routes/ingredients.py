"""
Ingredients API Routes
"""

import csv
import io
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_active_user, require_sales
from app.crud import ingredients as crud_ingredients
from app.database import get_db
from app.models import Ingredient, User
from app.schemas.schemas import (
    IngredientCreate,
    IngredientResponse,
    IngredientUpdate,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[IngredientResponse])
async def get_ingredients(
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get paginated list of ingredients"""
    # TODO: Implement pagination and filtering
    total = db.query(Ingredient).count()
    ingredients = db.query(Ingredient).offset((page - 1) * size).limit(size).all()

    return {
        "items": ingredients,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }


@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get single ingredient by ID"""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return ingredient


@router.post("/", response_model=IngredientResponse)
async def create_ingredient(
    ingredient: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
):
    """Create new ingredient"""
    # Check if ingredient with same name/code exists
    existing = (
        db.query(Ingredient)
        .filter((Ingredient.name == ingredient.name) | (Ingredient.code == ingredient.code))
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingredient with this name or code already exists",
        )

    db_ingredient = Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)

    return db_ingredient


@router.put("/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient(
    ingredient_id: int,
    ingredient_update: IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
):
    """Update ingredient"""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    # Update only provided fields
    update_data = ingredient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)

    return ingredient


@router.delete("/{ingredient_id}")
async def delete_ingredient(
    ingredient_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_sales)
):
    """Delete ingredient"""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    # Check if ingredient is used in any blends
    # TODO: Add check for blend usage

    db.delete(ingredient)
    db.commit()

    return {"message": "Ingredient deleted successfully"}


@router.post("/import")
async def import_ingredients(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales),
):
    """Import ingredients from CSV file"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported"
        )

    contents = await file.read()
    csv_data = csv.DictReader(io.StringIO(contents.decode("utf-8")))

    imported = 0
    errors = []

    for row_num, row in enumerate(csv_data, start=2):
        try:
            # Validate and create ingredient
            ingredient_data = {
                "name": row["name"],
                "code": row.get("code"),
                "type": row["type"],
                "nitrogen": float(row.get("nitrogen", 0)),
                "phosphate": float(row.get("phosphate", 0)),
                "potash": float(row.get("potash", 0)),
                "cost_per_ton": float(row["cost_per_ton"]),
                # Add other fields as needed
            }

            ingredient = Ingredient(**ingredient_data)
            db.add(ingredient)
            imported += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    if imported > 0:
        db.commit()

    return {
        "imported": imported,
        "errors": errors,
        "message": f"Successfully imported {imported} ingredients",
    }


@router.get("/export/csv")
async def export_ingredients(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Export all ingredients to CSV"""
    ingredients = db.query(Ingredient).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "name",
            "code",
            "type",
            "nitrogen",
            "phosphate",
            "potash",
            "sulfur",
            "calcium",
            "magnesium",
            "cost_per_ton",
            "is_available",
        ]
    )

    # Write data
    for ing in ingredients:
        writer.writerow(
            [
                ing.name,
                ing.code,
                ing.type.value,
                ing.nitrogen,
                ing.phosphate,
                ing.potash,
                ing.sulfur,
                ing.calcium,
                ing.magnesium,
                ing.cost_per_ton,
                ing.is_available,
            ]
        )

    output.seek(0)

    return {
        "filename": f"ingredients_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "content": output.getvalue(),
        "content_type": "text/csv",
    }
