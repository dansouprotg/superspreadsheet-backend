from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.school_models import SkillStatus

class Milestone(BaseModel):
    id: int
    skill_name: str
    previous_status: SkillStatus | None
    new_status: SkillStatus
    comment: str | None
    progress_value: str | None
    narrative: str | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)