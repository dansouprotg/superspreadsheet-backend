from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.school_models import SkillStatus

class SkillBase(BaseModel):
    name: str
    current_status: SkillStatus
    score: int = 0  # Default score

class Skill(SkillBase):
    id: int
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SkillUpdate(BaseModel):
    new_status: SkillStatus | None = None
    score: int | None = None
    comment: str | None = None
    progress_value: str | None = None