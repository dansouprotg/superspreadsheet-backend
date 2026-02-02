from sqlalchemy.orm import Session
from app.models.school_models import Skill, Milestone, Student, SkillStatus
from app.schemas.skill_schema import SkillUpdate

def _generate_narrative(student_name: str, skill_name: str, new_status: SkillStatus, progress_value: str | None):
    templates = {
        SkillStatus.RED: f"{student_name} needs attention in {skill_name}.",
        SkillStatus.YELLOW: f"{student_name} is now progressing in {skill_name}.",
        SkillStatus.GREEN: f"{student_name} has shown good performance in {skill_name}.",
        SkillStatus.GOLD: f"{student_name} has exceeded expectations in {skill_name}!",
    }
    narrative = templates.get(new_status, f"{student_name}'s {skill_name} skill was updated.")
    
    if progress_value:
        narrative += f" They can now handle a '{progress_value}'."
        
    return narrative

def update_student_skill(db: Session, student_id: int, skill_name: str, update_data: SkillUpdate):
    skill = db.query(Skill).join(Student).filter(Skill.student_id == student_id, Skill.name == skill_name).first()
    if not skill:
        return None

    previous_status = skill.current_status
    
    # Generate the automated narrative
    narrative = _generate_narrative(
        student_name=skill.student.name,
        skill_name=skill_name,
        new_status=update_data.new_status,
        progress_value=update_data.progress_value
    )

    milestone = Milestone(
        student_id=student_id,
        skill_name=skill_name,
        previous_status=previous_status,
        new_status=update_data.new_status,
        comment=update_data.comment,
        progress_value=update_data.progress_value,
        narrative=narrative # Save the narrative to the database
    )
    db.add(milestone)
    
    skill.current_status = update_data.new_status
    
    db.commit()
    db.refresh(skill)
    
    return skill