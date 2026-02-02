from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.user_model import User
from app.models.school_models import Class, Student

# from app.routers import auth_router, user_router, class_router, skill_router, student_router, analytics_router, export_router # Import new router

app = FastAPI()

# ... (origins and middleware code is the same)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth_router.router)
# app.include_router(user_router.router)
# app.include_router(class_router.router)
# app.include_router(skill_router.router)
# app.include_router(student_router.router)
# app.include_router(analytics_router.router)
# app.include_router(export_router.router) # Add new router

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Progress Tracking API"}