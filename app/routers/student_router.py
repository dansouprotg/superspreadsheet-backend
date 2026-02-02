from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.student_schema import Student, StudentPromote # Import StudentPromote
from app.crud import student_crud, class_crud
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/students",
    tags=["students"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/{student_id}", response_model=Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = student_crud.get_student_by_id(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

# --- ADD THIS NEW ENDPOINT ---
@router.put("/{student_id}/promote", response_model=Student)
def promote_student_to_new_class(student_id: int, promotion: StudentPromote, db: Session = Depends(get_db)):
    # Check if the target class exists
    target_class = class_crud.get_class(db, class_id=promotion.new_class_id)
    if not target_class:
        raise HTTPException(status_code=404, detail="Target class not found")

    updated_student = student_crud.promote_student(db=db, student_id=student_id, new_class_id=promotion.new_class_id)
    if updated_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student