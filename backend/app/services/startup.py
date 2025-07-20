"""
SurBlend Startup Service
Database initialization and default data creation
"""

import logging
import os
from decimal import Decimal
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app.database import get_db, test_connection, create_tables
from app.models import Ingredient, IngredientType, SystemSetting, User, UserRole
from app.auth.security import get_password_hash

logger = logging.getLogger(__name__)

load_dotenv()

async def initialize_database():
    """Initialize database and create tables"""
    logger.info("Initializing database...")
    try:
        if not await test_connection():
            raise Exception("Failed to connect to database")
        create_tables()
        db = next(get_db())  # Get a single session
        try:
            await initialize_system_settings(db)
            await create_default_admin(db)
            await load_sample_ingredients(db)
        finally:
            db.close()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def create_default_admin(db: Session):
    """Create default admin user if none exists"""
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            logger.info("Creating default admin user...")
            admin = User(
                username=os.getenv("ADMIN_USERNAME", "admin"),
                email=os.getenv("ADMIN_EMAIL", "jonmarsh@bullochfertilizer.com"),
                full_name="System Administrator",
                hashed_password=get_password_hash(os.getenv("ADMIN_PASSWORD", "Summer24!")),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Default admin user created (username: admin)")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
        db.rollback()
        raise

async def initialize_system_settings(db: Session):
    """Initialize default system settings"""
    try:
        default_settings = {
            "company_info": {
                "name": os.getenv("DEFAULT_COMPANY_NAME", "Bulloch Fertilizer Co., Inc."),
                "address": "123 Main Street",
                "city": "Your City",
                "state": "GA",
                "zip": "30458",
                "phone": "(912) 555-0000",
                "email": os.getenv("SMTP_FROM", "info@yourcompany.com"),
                "website": "www.yourcompany.com",
            },
            "quote_settings": {
                "default_margin_type": "percent",
                "default_margin_value": float(os.getenv("DEFAULT_MARGIN_PERCENT", 20.0)),
                "quote_validity_days": int(os.getenv("DEFAULT_QUOTE_VALIDITY_DAYS", 30)),
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
                    key=key,
                    value=str(value),  # Convert to string for storage
                    description=f"Default {key.replace('_', ' ').title()}"
                )
                db.add(setting)
        db.commit()
        logger.info("System settings initialized")
    except Exception as e:
        logger.error(f"Error initializing system settings: {e}")
        db.rollback()
        raise

async def load_sample_ingredients(db: Session):
    """Load sample ingredient data"""
    try:
        if db.query(Ingredient).count() > 0:
            logger.info("Ingredients already exist, skipping sample data")
            return

        sample_ingredients = [
            {
                "name": "Urea",
                "code": "UREA",
                "type": IngredientType.NUTRIENT,
                "nitrogen": Decimal("46.0"),
                "density": 48.0,
                "cost_per_ton": Decimal("580.00"),
                "source": "Granular",
            },
            {
                "name": "Ammonium Sulfate",
                "code": "AMS",
                "type": IngredientType.NUTRIENT,
                "nitrogen": Decimal("21.0"),
                "sulfur": Decimal("24.0"),
                "density": 62.0,
                "cost_per_ton": Decimal("385.00"),
                "source": "Granular",
            },
            {
                "name": "UAN 32%",
                "code": "UAN32",
                "type": IngredientType.NUTRIENT,
                "nitrogen": Decimal("32.0"),
                "density": 11.06,
                "cost_per_ton": Decimal("425.00"),
                "source": "Liquid",
            },
            {
                "name": "DAP (18-46-0)",
                "code": "DAP",
                "type": IngredientType.NUTRIENT,
                "nitrogen": Decimal("18.0"),
                "phosphate": Decimal("46.0"),
                "density": 60.0,
                "cost_per_ton": Decimal("685.00"),
                "source": "Granular",
            },
            {
                "name": "MAP (11-52-0)",
                "code": "MAP",
                "type": IngredientType.NUTRIENT,
                "nitrogen": Decimal("11.0"),
                "phosphate": Decimal("52.0"),
                "density": 60.0,
                "cost_per_ton": Decimal("735.00"),
                "source": "Granular",
            },
            {
                "name": "Muriate of Potash",
                "code": "MOP",
                "type": IngredientType.NUTRIENT,
                "potash": Decimal("60.0"),
                "density": 64.0,
                "cost_per_ton": Decimal("520.00"),
                "source": "Granular",
            },
            {
                "name": "Sulfate of Potash",
                "code": "SOP",
                "type": IngredientType.NUTRIENT,
                "potash": Decimal("50.0"),
                "sulfur": Decimal("18.0"),
                "density": 75.0,
                "cost_per_ton": Decimal("780.00"),
                "source": "Granular",
            },
            {
                "name": "Zinc Sulfate",
                "code": "ZNSO4",
                "type": IngredientType.NUTRIENT,
                "zinc": Decimal("35.5"),
                "sulfur": Decimal("17.5"),
                "density": 70.0,
                "cost_per_ton": Decimal("1250.00"),
                "source": "Granular",
            },
            {
                "name": "Boron 15%",
                "code": "BORON",
                "type": IngredientType.NUTRIENT,
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
        raise

async def check_system_health():
    """Check system health and requirements"""
    checks = {"database": False, "disk_space": False, "memory": False, "python_version": False}
    try:
        checks["database"] = await test_connection()
        import shutil
        stat = shutil.disk_usage("/")
        checks["disk_space"] = (stat.free / (1024 * 1024 * 1024)) > 1.0
        import psutil
        mem = psutil.virtual_memory()
        checks["memory"] = (mem.available / (1024 * 1024)) > 500
        import sys
        checks["python_version"] = sys.version_info >= (3, 11)
        logger.info(f"System health check: {checks}")
        return checks
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return checks
