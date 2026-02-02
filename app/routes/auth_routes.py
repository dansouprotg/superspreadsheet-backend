from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from pydantic import ValidationError

from app.database import SessionLocal
from app.schemas.user_schema import Token, UserCreate, SetupRequest, SetupComplete, UserLogin
from app.crud import user_crud
from app.email_utils import send_verification_email, verification_codes
from app.models.user_model import User

auth_bp = Blueprint('auth', __name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise

@auth_bp.route("/api/auth/setup/request-code", methods=["POST"])
def request_setup_code():
    db = SessionLocal()
    try:
        data = request.get_json()
        try:
            req_data = SetupRequest(**data)
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422

        if db.query(User).count() > 0:
            return jsonify({"detail": "An admin account already exists. Setup is not allowed."}), 403

        send_verification_email(req_data.email)
        return jsonify({"message": "Verification code sent successfully."})
    finally:
        db.close()

@auth_bp.route("/api/auth/setup/complete", methods=["POST"])
def complete_setup():
    db = SessionLocal()
    try:
        data = request.get_json()
        try:
            req_data = SetupComplete(**data)
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422

        if db.query(User).count() > 0:
            return jsonify({"detail": "An admin account already exists. Setup is not allowed."}), 403

        stored_code = verification_codes.get(req_data.email)
        if not stored_code or stored_code != req_data.code:
             return jsonify({"detail": "Invalid or expired verification code."}), 400

        user_data = UserCreate(email=req_data.email, password=req_data.password)
        user_crud.create_user(db, user_data)
        del verification_codes[req_data.email]
        return jsonify({"message": "Setup complete. You can now log in."})
    except IntegrityError:
         return jsonify({"detail": "User likely already exists."}), 400
    finally:
        db.close()

@auth_bp.route("/token", methods=["POST"])
def login_for_access_token():
    db = SessionLocal()
    try:
        # Flask doesn't have OAuth2PasswordRequestForm auto-parsing
        # We expect form data or JSON. Let's support JSON mainly for modern frontend, 
        # or form data if adhering strictly to OAuth2.
        # Ideally frontends send JSON: { "username": "...", "password": "..." }
        data = request.get_json(silent=True)
        if not data:
            # Fallback to form data
            data = request.form
        
        username = data.get("username") or data.get("email") # Support both
        password = data.get("password")

        if not username or not password:
             return jsonify({"detail": "Missing username or password"}), 400

        user = user_crud.get_user_by_email(db, email=username)
        if not user or not pwd_context.verify(password, user.hashed_password):
            return jsonify({"detail": "Incorrect email or password"}), 401
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return jsonify({"access_token": access_token, "token_type": "bearer"})
    finally:
        db.close()
