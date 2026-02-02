from sqlalchemy.orm import Session
from app.models.school_models import Student, Skill, SkillStatus # Import SkillStatus
from app.schemas.student_schema import StudentCreate

def get_student_by_id(db: Session, student_id: int):
    return db.query(Student).filter(Student.id == student_id).first()

def promote_student(db: Session, student_id: int, new_class_id: int):
    db_student = get_student_by_id(db, student_id=student_id)
    if not db_student:
        return None
    
    # 1. Update the student's class
    db_student.class_id = new_class_id
    
    # --- THIS IS THE NEW LOGIC ---
    # 2. Reset all of the student's skills to the default status
    for skill in db_student.skills:
        skill.current_status = SkillStatus.RED
    # --- END OF NEW LOGIC ---

    db.commit()
    db.refresh(db_student)
    return db_student

def create_student_for_class(db: Session, student: StudentCreate, class_id: int):
    db_student = Student(name=student.name, class_id=class_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    skill_names = ["Listening", "Reading", "Speaking", "Writing"]
    for name in skill_names:
        skill = Skill(name=name, student_id=db_student.id)
        db.add(skill)
    
    db.commit()
    db.refresh(db_student)
    return db_student