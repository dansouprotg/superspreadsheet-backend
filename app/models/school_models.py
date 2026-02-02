from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class SkillStatus(str, enum.Enum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    GOLD = "Gold"

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    students = relationship("Student", back_populates="enrolled_class", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    enrollment_date = Column(Date, default=func.now())
    class_id = Column(Integer, ForeignKey("classes.id"))
    enrolled_class = relationship("Class", back_populates="students")
    skills = relationship("Skill", back_populates="student", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="student", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    current_status = Column(Enum(SkillStatus), default=SkillStatus.RED)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    student_id = Column(Integer, ForeignKey("students.id"))
    student = relationship("Student", back_populates="skills")

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(50), nullable=False)
    previous_status = Column(Enum(SkillStatus))
    new_status = Column(Enum(SkillStatus), nullable=False)
    comment = Column(String(1024))
    progress_value = Column(String(255))
    # --- ADD THIS NEW COLUMN ---
    narrative = Column(String(1024))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    student_id = Column(Integer, ForeignKey("students.id"))
    student = relationship("Student", back_populates="milestones")