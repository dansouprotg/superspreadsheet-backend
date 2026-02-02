from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User

router = APIRouter()

@router.get("/api/users/exists")
def user_exists(db: Session = Depends(get_db)):
    user_count = db.query(User).count()
    return {"user_exists": user_count > 0}