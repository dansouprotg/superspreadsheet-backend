from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from app.models.school_models import Student, Skill, Milestone, SkillStatus
from datetime import datetime, timedelta

# --- Weighted Score Calculation ---
SCORE_MAP = {SkillStatus.RED: 1, SkillStatus.YELLOW: 2, SkillStatus.GREEN: 3, SkillStatus.GOLD: 4}

def _get_student_weighted_score(student: Student):
    if not student.skills:
        return 1.0
    total_score = sum(SCORE_MAP[skill.current_status] for skill in student.skills)
    return total_score / len(student.skills)

def _map_score_to_category(score: float):
    if 1.0 <= score < 2.0: return "red"
    if 2.0 <= score < 2.6: return "yellow"
    if 2.6 <= score < 3.3: return "green"
    return "gold"

# --- A. Analytics by Skill ---
def get_analytics_by_skill(db: Session, class_id: int):
    skills_query = db.query(Skill.name, Skill.current_status, func.count(Skill.id)).join(Student).filter(Student.class_id == class_id).group_by(Skill.name, Skill.current_status).all()
    
    result = {
        "listening": {"red": 0, "yellow": 0, "green": 0, "gold": 0},
        "reading": {"red": 0, "yellow": 0, "green": 0, "gold": 0},
        "speaking": {"red": 0, "yellow": 0, "green": 0, "gold": 0},
        "writing": {"red": 0, "yellow": 0, "green": 0, "gold": 0},
    }
    
    for skill_name, status, count in skills_query:
        result[skill_name.lower()][status.name.lower()] = count
        
    return result

# --- B. Weighted Student Distribution ---
def get_weighted_student_distribution(db: Session, class_id: int):
    students = db.query(Student).options(joinedload(Student.skills)).filter(Student.class_id == class_id).all()
    distribution = {"red": 0, "yellow": 0, "green": 0, "gold": 0}

    for student in students:
        score = _get_student_weighted_score(student)
        category = _map_score_to_category(score)
        distribution[category] += 1
        
    return distribution

# --- D. Trend Analytics ---
def get_skill_trends(db: Session, class_id: int, days: int = 30):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    milestones = db.query(Milestone).join(Student).filter(Student.class_id == class_id, Milestone.timestamp >= start_date).all()
    
    trends = {
        "listening": {"improvements": 0, "declines": 0},
        "reading": {"improvements": 0, "declines": 0},
        "speaking": {"improvements": 0, "declines": 0},
        "writing": {"improvements": 0, "declines": 0},
    }

    for milestone in milestones:
        if milestone.previous_status is None: continue
        
        prev_score = SCORE_MAP.get(milestone.previous_status, 0)
        new_score = SCORE_MAP.get(milestone.new_status, 0)
        
        if new_score > prev_score:
            trends[milestone.skill_name.lower()]["improvements"] += 1
        elif new_score < prev_score:
            trends[milestone.skill_name.lower()]["declines"] += 1
            
    return trends

# --- E. Student Comparison / Helper ---
def get_class_average_scores(db: Session, class_id: int):
    avg_scores_query = db.query(Skill.name, func.avg(
        case(
            (Skill.current_status == SkillStatus.RED, 1),
            (Skill.current_status == SkillStatus.YELLOW, 2),
            (Skill.current_status == SkillStatus.GREEN, 3),
            (Skill.current_status == SkillStatus.GOLD, 4)
        )
    )).join(Student).filter(Student.class_id == class_id).group_by(Skill.name).all()
    
    return {name.lower(): avg for name, avg in avg_scores_query}

# --- THIS IS THE RESTORED FUNCTION ---
def get_student_analytics(db: Session, student_id: int):
    query = (
        db.query(Skill.current_status, func.count(Skill.id))
        .filter(Skill.student_id == student_id)
        .group_by(Skill.current_status)
        .all()
    )
    
    analytics = {status.name: 0 for status in SkillStatus}
    for status, count in query:
        analytics[status.name] = count
        
    total_skills = sum(analytics.values())

    response = {
        "red": {"count": analytics["RED"], "percentage": (analytics["RED"] / total_skills * 100) if total_skills > 0 else 0},
        "yellow": {"count": analytics["YELLOW"], "percentage": (analytics["YELLOW"] / total_skills * 100) if total_skills > 0 else 0},
        "green": {"count": analytics["GREEN"], "percentage": (analytics["GREEN"] / total_skills * 100) if total_skills > 0 else 0},
        "gold": {"count": analytics["GOLD"], "percentage": (analytics["GOLD"] / total_skills * 100) if total_skills > 0 else 0},
        "total": total_skills
    }
    
    return response