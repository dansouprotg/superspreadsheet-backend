from pydantic import BaseModel, ConfigDict
from typing import List
from .student_schema import Student

class ClassBase(BaseModel):
    name: str

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int
    students: List[Student] = []

    model_config = ConfigDict(from_attributes=True)