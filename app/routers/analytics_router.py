from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import analytics_schema
from app.crud import analytics_crud, student_crud
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/class/{class_id}/by-skill", response_model=analytics_schema.AnalyticsBySkill)
def read_analytics_by_skill(class_id: int, db: Session = Depends(get_db)):
    return analytics_crud.get_analytics_by_skill(db, class_id=class_id)

@router.get("/class/{class_id}/weighted-distribution", response_model=analytics_schema.WeightedStudentDistribution)
def read_weighted_distribution(class_id: int, db: Session = Depends(get_db)):
    return analytics_crud.get_weighted_student_distribution(db, class_id=class_id)

@router.get("/class/{class_id}/trends", response_model=analytics_schema.SkillTrends)
def read_skill_trends(class_id: int, days: int = 30, db: Session = Depends(get_db)):
    return analytics_crud.get_skill_trends(db, class_id=class_id, days=days)

@router.get("/student/{student_id}/comparison", response_model=List[analytics_schema.StudentSkillAverage])
def read_student_comparison(student_id: int, db: Session = Depends(get_db)):
    student = student_crud.get_student_by_id(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_averages = analytics_crud.get_class_average_scores(db, class_id=student.class_id)
    
    comparison = []
    for skill in student.skills:
        comparison.append({
            "skill_name": skill.name,
            "student_score": analytics_crud.SCORE_MAP[skill.current_status],
            "class_average_score": class_averages.get(skill.name.lower(), 0)
        })
    return comparison