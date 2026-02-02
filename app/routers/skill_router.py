from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.skill_schema import Skill, SkillUpdate
from app.crud import skill_crud
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api",
    tags=["skills"],
    dependencies=[Depends(get_current_user)]
)

@router.put("/students/{student_id}/skills/{skill_name}", response_model=Skill)
def update_skill_for_student(student_id: int, skill_name: str, skill_update: SkillUpdate, db: Session = Depends(get_db)):
    updated_skill = skill_crud.update_student_skill(db=db, student_id=student_id, skill_name=skill_name, update_data=skill_update)
    if updated_skill is None:
        raise HTTPException(status_code=404, detail="Student or Skill not found")
    return updated_skill