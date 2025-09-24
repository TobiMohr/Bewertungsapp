from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .criterias import CriterionRead

class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None

class SessionCreate(SessionBase):
    criteria: Optional[List[int]] = []

class SessionUpdate(SessionBase):
    criteria: Optional[List[int]] = []

class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    criteria: List[CriterionRead] = []

    class Config:
        orm_mode = True
