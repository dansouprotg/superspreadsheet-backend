from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    enrollment_date = Column(Date, default=date.today)
    class_id = Column(Integer, ForeignKey("classes.id"))

    # We've renamed the confusing 'class_' to 'enrolled_class' for clarity and to fix the issue
    enrolled_class = relationship("Class", back_populates="students")