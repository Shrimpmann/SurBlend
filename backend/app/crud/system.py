from sqlalchemy.orm import Session
from app.models import SystemSetting
from app.schemas import schemas

def get_system_settings(db: Session):
    return db.query(SystemSetting).all()

def get_system_setting_by_key(db: Session, key: str):
    return db.query(SystemSetting).filter(SystemSetting.key == key).first()

def create_system_setting(db: Session, setting: schemas.SystemSettingUpdate):
    db_setting = SystemSetting(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting
