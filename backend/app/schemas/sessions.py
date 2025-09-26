# schemas/sessions.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .criterias import CriterionRead

class CriterionWithWeightRead(BaseModel):
    criterion: CriterionRead
    weight: int

    class Config:
        orm_mode = True


class CriterionWithWeightCreate(BaseModel):
    id: int
    weight: int = 1


class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None


class SessionCreate(SessionBase):
    criteria: Optional[List[CriterionWithWeightCreate]] = []


class SessionUpdate(SessionBase):
    criteria: Optional[List[CriterionWithWeightCreate]] = []


class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    session_criteria_assoc: List[CriterionWithWeightRead] = []

    class Config:
        orm_mode = True 
