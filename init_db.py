from app.database import engine, Base
from app.models.user_model import User
from app.models.school_models import Class, Student, Skill, Milestone

print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
