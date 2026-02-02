from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")



if not DATABASE_URL:
    # Fallback to a local SQLite database if valid URL is not provided
    # This prevents the NoneType error on startup if .env is missing/unloaded
    DATABASE_URL = "sqlite:///./sql_app.db"

# DATABASE_URL = "sqlite:///./sql_app.db"

# if DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine = None
SessionLocal = None

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()