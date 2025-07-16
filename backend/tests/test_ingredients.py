"""
Test cases for ingredients endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import Ingredient, IngredientType
from app.auth.security import create_access_token

@pytest.fixture
def auth_headers():
    """Create authentication headers for tests"""
    token = create_access_token(data={"sub": "testuser", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_create_ingredient(client: TestClient, db: Session, auth_headers):
    """Test creating a new ingredient"""
    ingredient_data = {
        "name": "Test Urea",
        "code": "UREA-TEST",
        "type": "dry",
        "nitrogen": 46.0,
        "phosphate": 0.0,
        "potash": 0.0,
        "cost_per_ton": 580.00
    }
    
    response = client.post(
        "/api/ingredients/",
        json=ingredient_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == ingredient_data["name"]
    assert data["nitrogen"] == ingredient_data["nitrogen"]
    assert "id" in data

def test_get_ingredients(client: TestClient, db: Session, auth_headers):
    """Test getting list of ingredients"""
    # Create test ingredients
    for i in range(5):
        ingredient = Ingredient(
            name=f"Test Ingredient {i}",
            code=f"TEST-{i}",
            type=IngredientType.DRY,
            cost_per_ton=100.00 * (i + 1)
        )
        db.add(ingredient)
    db.commit()
    
    response = client.get("/api/ingredients/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 5

def test_update_ingredient(client: TestClient, db: Session, auth_headers):
    """Test updating an ingredient"""
    # Create ingredient
    ingredient = Ingredient(
        name="Original Name",
        code="ORIG",
        type=IngredientType.DRY,
        cost_per_ton=500.00
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    
    # Update it
    update_data = {
        "name": "Updated Name",
        "cost_per_ton": 600.00
    }
    
    response = client.put(
        f"/api/ingredients/{ingredient.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert float(data["cost_per_ton"]) == 600.00

def test_delete_ingredient(client: TestClient, db: Session, auth_headers):
    """Test deleting an ingredient"""
    # Create ingredient
    ingredient = Ingredient(
        name="To Delete",
        code="DELETE",
        type=IngredientType.DRY,
        cost_per_ton=100.00
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    
    response = client.delete(
        f"/api/ingredients/{ingredient.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify it's deleted
    deleted = db.query(Ingredient).filter(Ingredient.id == ingredient.id).first()
    assert deleted is None

def test_import_csv(client: TestClient, auth_headers):
    """Test importing ingredients from CSV"""
    csv_content = """name,code,type,nitrogen,phosphate,potash,cost_per_ton
Imported Urea,IMP-UREA,dry,46,0,0,580
Imported DAP,IMP-DAP,dry,18,46,0,685"""
    
    files = {"file": ("ingredients.csv", csv_content, "text/csv")}
    
    response = client.post(
        "/api/ingredients/import",
        files=files,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 2
    assert len(data["errors"]) == 0