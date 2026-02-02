from flask import Blueprint, jsonify
from app.database import SessionLocal
from app.models.user_model import User

user_bp = Blueprint('user', __name__)

@user_bp.route("/api/users/exists", methods=["GET"])
def user_exists():
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        return jsonify({"user_exists": user_count > 0})
    finally:
        db.close()
