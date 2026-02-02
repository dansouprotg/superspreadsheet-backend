from flask import Blueprint, jsonify, request
from app.database import SessionLocal
from app.crud import analytics_crud, student_crud

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/api/analytics/class/<int:class_id>/by-skill", methods=["GET"])
def read_analytics_by_skill(class_id):
    db = SessionLocal()
    try:
        # The frontend expects a dictionary: {"listening": {"red": 0...}, ...}
        # CRUD returns exactly this structure.
        result = analytics_crud.get_analytics_by_skill(db, class_id=class_id)
        return jsonify(result)
    finally:
        db.close()

@analytics_bp.route("/api/analytics/class/<int:class_id>/weighted-distribution", methods=["GET"])
def read_weighted_distribution(class_id):
    db = SessionLocal()
    try:
        result = analytics_crud.get_weighted_student_distribution(db, class_id=class_id)
        # Frontend expects: { "red": X, "yellow": Y... }
        # CRUD returns exactly this structure.
        return jsonify(result)
    finally:
        db.close()

@analytics_bp.route("/api/analytics/class/<int:class_id>/trends", methods=["GET"])
def read_skill_trends(class_id):
    db = SessionLocal()
    try:
        days = int(request.args.get('days', 30))
        result = analytics_crud.get_skill_trends(db, class_id=class_id, days=days)
        # Frontend expects: { "listening": {"improvements": X, "declines": Y}, ... }
        # CRUD returns exactly this structure.
        return jsonify(result)
    finally:
        db.close()

@analytics_bp.route("/api/analytics/student/<int:student_id>/comparison", methods=["GET"])
def read_student_comparison(student_id):
    db = SessionLocal()
    try:
        student = student_crud.get_student_by_id(db, student_id=student_id)
        if not student:
             return jsonify({"detail": "Student not found"}), 404

        class_averages = analytics_crud.get_class_average_scores(db, class_id=student.class_id)
        
        comparison = []
        for skill in student.skills:
             # Need to map Enum to Score if not done in CRUD or if strictly using schemas
             # Replicating logic from router:
             score = analytics_crud.SCORE_MAP.get(skill.current_status, 0)
             comparison.append({
                "skill_name": skill.name,
                "student_score": score,
                "class_average_score": float(class_averages.get(skill.name.lower()) or 0.0)
            })
        return jsonify(comparison)
    finally:
        db.close()
