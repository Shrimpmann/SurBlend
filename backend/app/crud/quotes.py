from sqlalchemy.orm import Session
from app.models import Quote
from app.schemas import schemas

def get_quotes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Quote).offset(skip).limit(limit).all()

def get_quote_by_id(db: Session, quote_id: int):
    return db.query(Quote).filter(Quote.id == quote_id).first()

def create_quote(db: Session, quote: schemas.QuoteCreate):
    db_quote = Quote(**quote.dict(exclude={'services'}))
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote
