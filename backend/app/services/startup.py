"""
SurBlend Startup Service
Database initialization and default data creation
"""

import json
import logging
import os
from decimal import Decimal

from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.database import SessionLocal, create_tables, engine, test_connection
from app.models import Ingredient, IngredientType, SystemSetting, User, UserRole

logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize database and create tables"""
    logger.info("Initializing database...")

    # Test connection
    if not await test_connection():
        raise Exception("Failed to connect to database")

    # Create tables
    create_tables()

    # Initialize system settings
    await initialize_system_settings()

    logger.info("Database initialization complete")


async def create_default_admin():
    """Create default admin user if none exists"""
    db = SessionLocal()
    try:
        # Check if any admin exists
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()

        if not admin_exists:
            logger.info("Creating default admin user...")

            default_admin = User(
                username="admin",
                email=os.getenv("ADMIN_EMAIL", "admin@surblend.local"),
                full_name="System Administrator",
                hashed_password=get_password_hash(os.getenv("ADMIN_PASSWORD", "SurBlend2025!")),
                role=UserRole.ADMIN,
                is_active=True,
            )

            db.add(default_admin)
            db.commit()

            logger.info("Default admin user created (username: admin)")
        else:
            logger.info("Admin user already exists")

    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()


async def initialize_system_settings():
    """Initialize default system settings"""
    db = SessionLocal()
    try:
        default_settings = {
            "company_info": {
                "name": "Your Company Name",
                "address": "123 Main Street",
                "city": "Your City",
                "state": "GA",
                "zip": "30458",
                "phone": "(912) 555-0000",
                "email": "info@yourcompany.com",
                "website": "www.yourcompany.com",
            },
            "quote_settings": {
                "default_margin_type": "percent",
                "default_margin_value": 20.0,
                "quote_validity_days": 30,
                "price_rounding": 2.50,
                "min_order_quantity": 1.0,
                "quote_number_prefix": "Q",
                "quote_number_format": "Q-{year}{month:02d}-{number:04d}",
            },
            "blend_settings": {
                "default_application_rate": 200.0,
                "default_application_unit": "lbs/acre",
                "allow_custom_blends": True,
                "require_blend_approval": False,
            },
            "pdf_settings": {
                "logo_url": "",
                "header_color": "#1e40af",
                "show_guaranteed_analysis": True,
                "show_application_instructions": True,
                "footer_text": "Thank you for your business!",
            },
            "services": {
                "available_services": [
                    {"name": "Bagging", "default_cost": 5.00, "unit": "per ton"},
                    {"name": "Delivery", "default_cost": 3.50, "unit": "per mile"},
                    {"name": "Custom Application", "default_cost": 12.00, "unit": "per acre"},
                    {"name": "Soil Testing", "default_cost": 25.00, "unit": "per sample"},
                ]
            },
            "security": {
                "password_min_length": 8,
                "password_require_uppercase": True,
                "password_require_number": True,
                "session_timeout_minutes": 60,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
            },
        }

        for key, value in default_settings.items():
            existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if not existing:
                setting = SystemSetting(
                    key=key, value=value, description=f"Default {key.replace('_', ' ').title()}"
                )
                db.add(setting)

        db.commit()
        logger.info("System settings initialized")

    except Exception as e:
        logger.error(f"Error initializing system settings: {e}")
        db.rollback()
    finally:
        db.close()


async def load_sample_ingredients():
    """Load sample ingredient data"""
    db = SessionLocal()
    try:
        # Check if ingredients already exist
        if db.query(Ingredient).count() > 0:
            logger.info("Ingredients already exist, skipping sample data")
            return

        sample_ingredients = [
            # Nitrogen sources
            {
                "name": "Urea",
                "code": "UREA",
                "type": IngredientType.DRY,
                "nitrogen": Decimal("46.0"),
                "density": 48.0,
                "cost_per_ton": Decimal("580.00"),
                "source": "Granular",
            },
            {
                "name": "Ammonium Sulfate",
                "code": "AMS",
                "type": IngredientType.DRY,
                "nitrogen": Decimal("21.0"),
                "sulfur": Decimal("24.0"),
                "density": 62.0,
                "cost_per_ton": Decimal("385.00"),
                "source": "Granular",
            },
            {
                "name": "UAN 32%",
                "code": "UAN32",
                "type": IngredientType.LIQUID,
                "nitrogen": Decimal("32.0"),
                "density": 11.06,  # lbs/gal
                "cost_per_ton": Decimal("425.00"),
                "source": "Liquid",
            },
            # Phosphate sources
            {
                "name": "DAP (18-46-0)",
                "code": "DAP",
                "type": IngredientType.DRY,
                "nitrogen": Decimal("18.0"),
                "phosphate": Decimal("46.0"),
                "density": 60.0,
                "cost_per_ton": Decimal("685.00"),
                "source": "Granular",
            },
            {
                "name": "MAP (11-52-0)",
                "code": "MAP",
                "type": IngredientType.DRY,
                "nitrogen": Decimal("11.0"),
                "phosphate": Decimal("52.0"),
                "density": 60.0,
                "cost_per_ton": Decimal("735.00"),
                "source": "Granular",
            },
            # Potash sources
            {
                "name": "Muriate of Potash",
                "code": "MOP",
                "type": IngredientType.DRY,
                "potash": Decimal("60.0"),
                "density": 64.0,
                "cost_per_ton": Decimal("520.00"),
                "source": "Granular",
            },
            {
                "name": "Sulfate of Potash",
                "code": "SOP",
                "type": IngredientType.DRY,
                "potash": Decimal("50.0"),
                "sulfur": Decimal("18.0"),
                "density": 75.0,
                "cost_per_ton": Decimal("780.00"),
                "source": "Granular",
            },
            # Micronutrients
            {
                "name": "Zinc Sulfate",
                "code": "ZNSO4",
                "type": IngredientType.DRY,
                "zinc": Decimal("35.5"),
                "sulfur": Decimal("17.5"),
                "density": 70.0,
                "cost_per_ton": Decimal("1250.00"),
                "source": "Granular",
            },
            {
                "name": "Boron 15%",
                "code": "BORON",
                "type": IngredientType.DRY,
                "boron": Decimal("15.0"),
                "density": 55.0,
                "cost_per_ton": Decimal("2100.00"),
                "source": "Granular",
            },
        ]

        for ing_data in sample_ingredients:
            ingredient = Ingredient(**ing_data)
            db.add(ingredient)

        db.commit()
        logger.info(f"Loaded {len(sample_ingredients)} sample ingredients")

    except Exception as e:
        logger.error(f"Error loading sample ingredients: {e}")
        db.rollback()
    finally:
        db.close()


async def check_system_health():
    """Check system health and requirements"""
    checks = {"database": False, "disk_space": False, "memory": False, "python_version": False}

    # Check database
    checks["database"] = await test_connection()

    # Check disk space (require at least 1GB free)
    import shutil

    stat = shutil.disk_usage("/")
    checks["disk_space"] = (stat.free / (1024 * 1024 * 1024)) > 1.0

    # Check memory (require at least 500MB available)
    import psutil

    mem = psutil.virtual_memory()
    checks["memory"] = (mem.available / (1024 * 1024)) > 500

    # Check Python version
    import sys

    checks["python_version"] = sys.version_info >= (3, 11)

    return checks
