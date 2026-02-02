from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.database import SessionLocal
from app.schemas.class_schema import ClassCreate
from app.schemas.student_schema import StudentCreate
from app.crud import class_crud, student_crud, analytics_crud
from app.models.user_model import User

class_bp = Blueprint('classes', __name__)

@class_bp.route("/api/classes/", methods=["POST"])
def create_new_class():
    db = SessionLocal()
    try:
        data = request.get_json()
        try:
            class_obj = ClassCreate(**data)
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        
        new_class = class_crud.create_class(db=db, class_obj=class_obj)
        return jsonify({
            "id": new_class.id,
            "name": new_class.name
        })
    finally:
        db.close()

@class_bp.route("/api/classes/", methods=["GET"])
def read_classes():
    db = SessionLocal()
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        classes = class_crud.get_classes(db, skip=skip, limit=limit)
        
        result = []
        for c in classes:
            students_list = [{"id": s.id} for s in c.students] 
            analytics_data = analytics_crud.get_weighted_student_distribution(db, c.id)
            
            result.append({
                "id": c.id,
                "name": c.name,
                "students": students_list,
                "analytics_summary": analytics_data
            })

        return jsonify(result)
    finally:
        db.close()

@class_bp.route("/api/classes/<int:class_id>", methods=["GET"])
def read_class(class_id):
    db = SessionLocal()
    try:
        db_class = class_crud.get_class(db, class_id=class_id)
        if db_class is None:
            return jsonify({"detail": "Class not found"}), 404
        return jsonify({
            "id": db_class.id,
            "name": db_class.name
        })
    finally:
        db.close()

@class_bp.route("/api/classes/<int:class_id>/students", methods=["POST"])
def create_student_in_class(class_id):
    db = SessionLocal()
    try:
        db_class = class_crud.get_class(db, class_id=class_id)
        if db_class is None:
            return jsonify({"detail": "Class not found"}), 404
        
        data = request.get_json()
        try:
            student_data = StudentCreate(**data)
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422

        new_student = student_crud.create_student_for_class(db=db, student=student_data, class_id=class_id)
        return jsonify({
            "id": new_student.id,
            "name": new_student.name
        })
    finally:
        db.close()

@class_bp.route("/api/classes/<int:class_id>/students", methods=["GET"])
def read_class_students(class_id):
    db = SessionLocal()
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        
        students = student_crud.get_students_by_class_id(db, class_id=class_id, skip=skip, limit=limit, include_archived=include_archived)
        return jsonify([{
            "id": s.id,
            "name": s.name,
            "is_archived": s.is_archived,
            "skills": [{
                "id": skill.id,
                "name": skill.name,
                "current_status": skill.current_status.value if hasattr(skill.current_status, 'value') else skill.current_status,
                "score": skill.score,
                "last_updated": skill.last_updated
            } for skill in s.skills],
            "milestones": [{
                "id": m.id,
                "skill_name": m.skill_name,
                "new_status": m.new_status.value if hasattr(m.new_status, 'value') else m.new_status,
                "timestamp": m.timestamp
            } for m in s.milestones]
        } for s in students])
    finally:
        db.close()
