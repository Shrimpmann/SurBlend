from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL
import enum

Base = declarative_base()

class IngredientType(enum.Enum):
    NUTRIENT = "NUTRIENT"
    FILLER = "FILLER"
    ADDITIVE = "ADDITIVE"

class QuoteStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    VIEWER = "VIEWER"
    SALES_REP = "SALES_REP"

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, nullable=True)
    type = Column(Enum(IngredientType), nullable=False)
    nitrogen = Column(DECIMAL, default=0)
    phosphate = Column(DECIMAL, default=0)
    potash = Column(DECIMAL, default=0)
    sulfur = Column(DECIMAL, default=0)
    zinc = Column(DECIMAL, default=0)
    boron = Column(DECIMAL, default=0)
    density = Column(Float, nullable=True)
    cost_per_ton = Column(DECIMAL, nullable=False)
    source = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    email = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class Blend(Base):
    __tablename__ = "blends"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    blend_id = Column(Integer, ForeignKey("blends.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    margin_type = Column(String, default="percent")
    margin_value = Column(DECIMAL, nullable=False)
    unit_price = Column(DECIMAL, nullable=False)
    total_price = Column(DECIMAL, nullable=False)
    services_total = Column(DECIMAL, nullable=False)
    status = Column(Enum(QuoteStatus), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    sent_at = Column(DateTime)
    accepted_at = Column(DateTime)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
