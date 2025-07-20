from sqlalchemy.orm import Session
from app.models import Blend
from app.schemas import schemas

def get_blends(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Blend).offset(skip).limit(limit).all()

def get_blend_by_id(db: Session, blend_id: int):
    return db.query(Blend).filter(Blend.id == blend_id).first()

def create_blend(db: Session, blend: schemas.BlendCreate):
    db_blend = Blend(**blend.dict())
    db.add(db_blend)
    db.commit()
    db.refresh(db_blend)
    return db_blend
