from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List
from .skill_schema import Skill
from .milestone_schema import Milestone

class ClassInfo(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class StudentBase(BaseModel):
    name: str

class StudentCreate(StudentBase):
    pass

# --- ADD THIS NEW SCHEMA ---
class StudentPromote(BaseModel):
    new_class_id: int

class Student(StudentBase):
    id: int
    enrollment_date: date
    skills: List[Skill] = []
    milestones: List[Milestone] = []
    enrolled_class: ClassInfo
    model_config = ConfigDict(from_attributes=True)