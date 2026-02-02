from sqlalchemy.orm import Session
from app.models.school_models import Class
from app.schemas.class_schema import ClassCreate

def get_class(db: Session, class_id: int):
    return db.query(Class).filter(Class.id == class_id).first()

def get_classes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Class).offset(skip).limit(limit).all()

def create_class(db: Session, class_obj: ClassCreate):
    db_class = Class(name=class_obj.name)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class