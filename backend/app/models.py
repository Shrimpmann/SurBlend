"""
SurBlend Database Models
SQLAlchemy 2.0 models for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Text, JSON, Enum, DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SALES_REP = "sales_rep"
    VIEWER = "viewer"

class IngredientType(str, enum.Enum):
    DRY = "dry"
    LIQUID = "liquid"

class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Association tables
blend_ingredients = Table(
    'blend_ingredients',
    Base.metadata,
    Column('blend_id', Integer, ForeignKey('blends.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id')),
    Column('percentage', Float, nullable=False),
    Column('amount', Float, nullable=False)
)

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    quotes = relationship("Quote", back_populates="created_by_user")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True)
    type = Column(Enum(IngredientType), nullable=False)
    
    # Nutrient content (%)
    nitrogen = Column(DECIMAL(5, 2), default=0)
    phosphate = Column(DECIMAL(5, 2), default=0)  # P2O5
    potash = Column(DECIMAL(5, 2), default=0)     # K2O
    sulfur = Column(DECIMAL(5, 2), default=0)
    calcium = Column(DECIMAL(5, 2), default=0)
    magnesium = Column(DECIMAL(5, 2), default=0)
    boron = Column(DECIMAL(5, 2), default=0)
    iron = Column(DECIMAL(5, 2), default=0)
    manganese = Column(DECIMAL(5, 2), default=0)
    zinc = Column(DECIMAL(5, 2), default=0)
    copper = Column(DECIMAL(5, 2), default=0)
    molybdenum = Column(DECIMAL(5, 2), default=0)
    
    # Physical properties
    density = Column(Float)  # lbs/ft³ for dry, specific gravity for liquid
    moisture_content = Column(Float, default=0)
    
    # Pricing
    cost_per_ton = Column(DECIMAL(10, 2), nullable=False)
    margin_percent = Column(DECIMAL(5, 2), default=20)
    fixed_margin = Column(DECIMAL(10, 2))
    
    # Availability
    is_available = Column(Boolean, default=True)
    min_order_qty = Column(Float, default=0)
    max_order_qty = Column(Float)
    
    # Metadata
    source = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="ingredient")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    old_price = Column(DECIMAL(10, 2))
    new_price = Column(DECIMAL(10, 2))
    changed_by = Column(Integer, ForeignKey('users.id'))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text)
    
    # Relationships
    ingredient = relationship("Ingredient", back_populates="price_history")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    
    # Business info
    contact_person = Column(String(100))
    tax_id = Column(String(50))
    credit_limit = Column(DECIMAL(10, 2))
    payment_terms = Column(String(50), default="Net 30")
    
    # Preferences
    default_margin_type = Column(String(20), default="percent")  # percent or fixed
    default_margin_value = Column(DECIMAL(5, 2))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farms = relationship("Farm", back_populates="customer")
    quotes = relationship("Quote", back_populates="customer")

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    name = Column(String(200), nullable=False)
    location = Column(Text)
    total_acres = Column(Float)
    
    # Farm details
    soil_type = Column(String(100))
    irrigation_type = Column(String(100))
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="farms")
    fields = relationship("Field", back_populates="farm")

class Field(Base):
    __tablename__ = "fields"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey('farms.id'))
    name = Column(String(100), nullable=False)
    acres = Column(Float)
    crop_type = Column(String(100))
    planting_date = Column(DateTime)
    harvest_date = Column(DateTime)
    
    # Soil test data
    soil_test_date = Column(DateTime)
    soil_ph = Column(Float)
    soil_om = Column(Float)  # Organic matter %
    soil_cec = Column(Float)  # Cation Exchange Capacity
    
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="fields")

class Blend(Base):
    __tablename__ = "blends"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    description = Column(Text)
    
    # Blend properties
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Target nutrients (optional)
    target_n = Column(DECIMAL(5, 2))
    target_p = Column(DECIMAL(5, 2))
    target_k = Column(DECIMAL(5, 2))
    
    # Application info
    application_rate = Column(Float)  # lbs/acre
    application_unit = Column(String(20), default="lbs/acre")
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ingredients = relationship("Ingredient", secondary=blend_ingredients)
    quotes = relationship("Quote", back_populates="blend")

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    blend_id = Column(Integer, ForeignKey('blends.id'))
    
    # Quote details
    quantity = Column(Float, nullable=False)  # tons
    unit_price = Column(DECIMAL(10, 2))  # $/ton
    total_price = Column(DECIMAL(10, 2))
    
    # Margin applied
    margin_type = Column(String(20))  # percent or fixed
    margin_value = Column(DECIMAL(10, 2))
    
    # Additional services
    services = Column(JSON)  # {service_name: cost}
    services_total = Column(DECIMAL(10, 2), default=0)
    
    # Application info
    application_acres = Column(Float)
    cost_per_acre = Column(DECIMAL(10, 2))
    
    # Status
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    valid_until = Column(DateTime)
    
    # Notes
    internal_notes = Column(Text)
    customer_notes = Column(Text)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    sent_at = Column(DateTime)
    accepted_at = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="quotes")
    blend = relationship("Blend", back_populates="quotes")
    created_by_user = relationship("User", back_populates="quotes")

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
