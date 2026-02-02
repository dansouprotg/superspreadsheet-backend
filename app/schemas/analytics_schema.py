from pydantic import BaseModel
from typing import Dict

class SkillBreakdown(BaseModel):
    red: int
    yellow: int
    green: int
    gold: int

class AnalyticsBySkill(BaseModel):
    listening: SkillBreakdown
    reading: SkillBreakdown
    speaking: SkillBreakdown
    writing: SkillBreakdown

class WeightedStudentDistribution(BaseModel):
    red: int
    yellow: int
    green: int
    gold: int

class TrendData(BaseModel):
    improvements: int
    declines: int

class SkillTrends(BaseModel):
    listening: TrendData
    reading: TrendData
    speaking: TrendData
    writing: TrendData

class StudentSkillAverage(BaseModel):
    skill_name: str
    student_score: float
    class_average_score: float