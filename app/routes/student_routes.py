from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.database import SessionLocal
from app.schemas.student_schema import StudentPromote
from app.crud import student_crud, class_crud

student_bp = Blueprint('students', __name__)

@student_bp.route("/api/students/<int:student_id>", methods=["GET"])
def read_student(student_id):
    db = SessionLocal()
    try:
        db_student = student_crud.get_student_by_id(db, student_id=student_id)
        if db_student is None:
             return jsonify({"detail": "Student not found"}), 404
        
        # Manually serialize nested student data including skills and milestones
        # This mirrors the Pydantic schema structure
        student_dict = {
            "id": db_student.id,
            "name": db_student.name, # Assuming name is a property or composite of first/last
            "enrollment_date": db_student.enrollment_date,
            "is_archived": db_student.is_archived,
            "enrolled_class": {
                "id": db_student.enrolled_class.id,
                "name": db_student.enrolled_class.name
            } if db_student.enrolled_class else None,
            "skills": [{
                "id": s.id,
                "name": s.name,
                "current_status": s.current_status.value if hasattr(s.current_status, 'value') else s.current_status,
                "score": s.score,
                "last_updated": s.last_updated
            } for s in db_student.skills],
            "milestones": [{
                "id": m.id,
                "skill_name": m.skill_name,
                "new_status": m.new_status.value if hasattr(m.new_status, 'value') else m.new_status,
                "timestamp": m.timestamp
            } for m in db_student.milestones]
        }
        return jsonify(student_dict)
    finally:
        db.close()

@student_bp.route("/api/students/<int:student_id>/promote", methods=["PUT"])
def promote_student_to_new_class(student_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        try:
            promotion = StudentPromote(**data)
        except ValidationError as e:
             return jsonify({"detail": e.errors()}), 422

        target_class = class_crud.get_class(db, class_id=promotion.new_class_id)
        if not target_class:
             return jsonify({"detail": "Target class not found"}), 404

        updated_student = student_crud.promote_student(db=db, student_id=student_id, new_class_id=promotion.new_class_id)
        if updated_student is None:
             return jsonify({"detail": "Student not found"}), 404
        
        return jsonify({
             "id": updated_student.id,
             "enrolled_class": {
                 "id": updated_student.enrolled_class.id,
                 "name": updated_student.enrolled_class.name
             }
        })
    finally:
        db.close()

@student_bp.route("/api/students/<int:student_id>/archive", methods=["PUT"])
def archive_student_endpoint(student_id):
    db = SessionLocal()
    try:
        student = student_crud.archive_student(db, student_id)
        if not student:
             return jsonify({"detail": "Student not found"}), 404
        return jsonify({"id": student.id, "is_archived": student.is_archived})
    finally:
        db.close()

@student_bp.route("/api/students/<int:student_id>/restore", methods=["PUT"])
def restore_student_endpoint(student_id):
    db = SessionLocal()
    try:
        student = student_crud.restore_student(db, student_id)
        if not student:
             return jsonify({"detail": "Student not found"}), 404
        return jsonify({"id": student.id, "is_archived": student.is_archived})
    finally:
        db.close()
