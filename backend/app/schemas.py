from pydantic import BaseModel
from typing import List, Dict

class ChemicalCreate(BaseModel):
    name: str
    aiPercentage: float
    costPerUnit: float
    displayOrder: int

class ChemicalResponse(ChemicalCreate):
    id: int
    class Config:
        from_attributes = True

class BlendIngredient(BaseModel):
    ingredientId: int
    quantity: float

class BlendChemical(BaseModel):
    chemicalId: int
    aiPercentage: float

class BlendCreate(BaseModel):
    name: str
    ingredients: List[BlendIngredient]
    chemicals: List[BlendChemical]
    totalCost: float
    applicationRate: float
    nutrients: Dict[str, float]

class BlendResponse(BlendCreate):
    id: int
    class Config:
        from_attributes = True
