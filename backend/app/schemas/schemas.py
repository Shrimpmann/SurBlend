"""
SurBlend Pydantic Schemas
Data validation and serialization schemas
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator

# Import enums from models
from app.models import IngredientType, QuoteStatus, UserRole


# Base schemas with common configuration
class SurBlendBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# Ingredient schemas
class IngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    type: IngredientType

    # Nutrients
    nitrogen: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    phosphate: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    potash: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    sulfur: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    calcium: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    magnesium: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    boron: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    iron: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    manganese: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    zinc: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    copper: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    molybdenum: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    # Properties
    density: Optional[float] = Field(None, gt=0)
    moisture_content: float = Field(default=0, ge=0, le=100)

    # Pricing
    cost_per_ton: Decimal = Field(..., gt=0)
    margin_percent: Decimal = Field(default=Decimal("20"), ge=0, le=100)
    fixed_margin: Optional[Decimal] = Field(None, ge=0)

    # Availability
    is_available: bool = True
    min_order_qty: float = Field(default=0, ge=0)
    max_order_qty: Optional[float] = Field(None, gt=0)

    # Metadata
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[IngredientType] = None
    nitrogen: Optional[Decimal] = None
    phosphate: Optional[Decimal] = None
    potash: Optional[Decimal] = None
    sulfur: Optional[Decimal] = None
    calcium: Optional[Decimal] = None
    magnesium: Optional[Decimal] = None
    cost_per_ton: Optional[Decimal] = None
    margin_percent: Optional[Decimal] = None
    is_available: Optional[bool] = None


class IngredientResponse(IngredientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Customer schemas
class CustomerBase(BaseModel):
    name: str = Field(..., max_length=200)
    code: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)

    contact_person: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    payment_terms: str = Field(default="Net 30", max_length=50)

    default_margin_type: Optional[str] = Field(default="percent", pattern="^(percent|fixed)$")
    default_margin_value: Optional[Decimal] = Field(None, ge=0)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Farm schemas
class FarmBase(BaseModel):
    name: str = Field(..., max_length=200)
    location: Optional[str] = None
    total_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = Field(None, max_length=100)
    irrigation_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class FarmCreate(FarmBase):
    customer_id: int


class FarmResponse(FarmBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Blend schemas
class BlendIngredient(BaseModel):
    ingredient_id: int
    percentage: float = Field(..., ge=0, le=100)
    amount: float = Field(..., ge=0)


class BlendBase(BaseModel):
    name: str = Field(..., max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_template: bool = False

    target_n: Optional[Decimal] = Field(None, ge=0, le=100)
    target_p: Optional[Decimal] = Field(None, ge=0, le=100)
    target_k: Optional[Decimal] = Field(None, ge=0, le=100)

    application_rate: Optional[float] = Field(None, gt=0)
    application_unit: str = Field(default="lbs/acre", max_length=20)


class BlendCreate(BlendBase):
    ingredients: List[BlendIngredient]

    @validator("ingredients")
    def validate_ingredients(cls, v):
        if not v:
            raise ValueError("Blend must have at least one ingredient")

        total_percentage = sum(ing.percentage for ing in v)
        if abs(total_percentage - 100) > 0.01:  # Allow small rounding errors
            raise ValueError(
                f"Ingredient percentages must sum to 100% (current: {total_percentage}%)"
            )

        return v


class BlendResponse(BlendBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    # Calculated fields
    total_n: Optional[Decimal] = None
    total_p: Optional[Decimal] = None
    total_k: Optional[Decimal] = None
    cost_per_ton: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


# Quote schemas
class QuoteService(BaseModel):
    name: str
    cost: Decimal = Field(..., ge=0)


class QuoteBase(BaseModel):
    customer_id: int
    blend_id: int
    quantity: float = Field(..., gt=0)

    margin_type: str = Field(default="percent", pattern="^(percent|fixed)$")
    margin_value: Decimal = Field(..., ge=0)

    application_acres: Optional[float] = Field(None, gt=0)

    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None


class QuoteCreate(QuoteBase):
    services: Optional[List[QuoteService]] = []


class QuoteUpdate(BaseModel):
    quantity: Optional[float] = None
    margin_type: Optional[str] = None
    margin_value: Optional[Decimal] = None
    status: Optional[QuoteStatus] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None


class QuoteResponse(QuoteBase):
    id: int
    quote_number: str
    unit_price: Decimal
    total_price: Decimal
    services_total: Decimal
    cost_per_acre: Optional[Decimal]
    status: QuoteStatus
    valid_until: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Analytics schemas
class DashboardStats(BaseModel):
    total_quotes: int
    quotes_this_month: int
    total_customers: int
    active_ingredients: int
    total_revenue: Decimal
    average_margin: Decimal
    conversion_rate: float


class SalesRepStats(BaseModel):
    user_id: int
    user_name: str
    total_quotes: int
    total_revenue: Decimal
    average_margin: Decimal
    conversion_rate: float


# System schemas
class SystemSettingUpdate(BaseModel):
    value: Any


class SystemSettingResponse(BaseModel):
    key: str
    value: Any
    description: Optional[str]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# Import/Export schemas
class IngredientImport(BaseModel):
    ingredients: List[IngredientCreate]


class IngredientExport(BaseModel):
    ingredients: List[IngredientResponse]
    export_date: datetime
    total_count: int
