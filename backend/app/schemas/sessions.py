from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .criterias import CriterionRead

class CriterionWithWeight(BaseModel):
    id: int
    weight: int = 1

class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None

class SessionCreate(SessionBase):
    criteria: Optional[List[CriterionWithWeight]] = []

class SessionUpdate(SessionBase):
    criteria: Optional[List[CriterionWithWeight]] = []

class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    criteria: List[CriterionRead] = []

    class Config:
        orm_mode = True
