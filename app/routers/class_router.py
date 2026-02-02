from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.class_schema import Class, ClassCreate
from app.schemas.student_schema import Student, StudentCreate
from app.crud import class_crud, student_crud
from app.dependencies import get_current_user
from app.models.user_model import User

router = APIRouter(
    prefix="/api/classes",
    tags=["classes"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=Class)
def create_new_class(class_obj: ClassCreate, db: Session = Depends(get_db)):
    return class_crud.create_class(db=db, class_obj=class_obj)

@router.get("/", response_model=List[Class])
def read_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    classes = class_crud.get_classes(db, skip=skip, limit=limit)
    return classes

@router.get("/{class_id}", response_model=Class)
def read_class(class_id: int, db: Session = Depends(get_db)):
    db_class = class_crud.get_class(db, class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@router.post("/{class_id}/students", response_model=Student)
def create_student_in_class(class_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    db_class = class_crud.get_class(db, class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return student_crud.create_student_for_class(db=db, student=student, class_id=class_id)