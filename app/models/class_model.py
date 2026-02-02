from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    
    # The relationship is defined here, pointing to the 'enrolled_class' attribute in the Student model
    students = relationship("Student", back_populates="enrolled_class")