from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

from app.database import get_db
from app.schemas.user_schema import Token, UserCreate, SetupRequest, SetupComplete
from app.crud import user_crud
from app.email_utils import send_verification_email, verification_codes
from app.models.user_model import User

router = APIRouter()
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

def check_if_user_exists(db: Session):
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An admin account already exists. Setup is not allowed.",
        )

@router.post("/api/auth/setup/request-code")
async def request_setup_code(request: SetupRequest, db: Session = Depends(get_db)):
    check_if_user_exists(db)
    await send_verification_email(request.email)
    return {"message": "Verification code sent successfully."}

@router.post("/api/auth/setup/complete")
def complete_setup(request: SetupComplete, db: Session = Depends(get_db)):
    check_if_user_exists(db)
    stored_code = verification_codes.get(request.email)
    if not stored_code or stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code.",
        )
    
    user_data = UserCreate(email=request.email, password=request.password)
    user_crud.create_user(db, user_data)
    del verification_codes[request.email] # Clean up the used code
    return {"message": "Setup complete. You can now log in."}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}