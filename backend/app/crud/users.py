from sqlalchemy.orm import Session
from app.models import User
from app.schemas import schemas

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
