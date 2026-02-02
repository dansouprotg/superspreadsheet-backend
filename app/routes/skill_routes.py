from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.database import SessionLocal
from app.schemas.skill_schema import SkillUpdate
from app.crud import skill_crud

skill_bp = Blueprint('skills', __name__)

@skill_bp.route("/api/students/<int:student_id>/skills/<skill_name>", methods=["PUT"])
def update_skill_for_student(student_id, skill_name):
    db = SessionLocal()
    try:
        data = request.get_json()
        try:
            skill_update = SkillUpdate(**data)
        except ValidationError as e:
             return jsonify({"detail": e.errors()}), 422

        updated_skill = skill_crud.update_student_skill(db=db, student_id=student_id, skill_name=skill_name, update_data=skill_update)
        if updated_skill is None:
             return jsonify({"detail": "Student or Skill not found"}), 404
        
        # Serialize simply
        return jsonify({
            "id": updated_skill.id,
            "name": updated_skill.name,
            "current_status": updated_skill.current_status.value if hasattr(updated_skill.current_status, 'value') else updated_skill.current_status,
            "score": updated_skill.score,
            "last_updated": updated_skill.last_updated
        })
    finally:
        db.close()
