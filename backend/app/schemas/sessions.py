from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .criterias import CriterionWithWeightCreate, CriterionWithWeightRead


# --- Session Base ---
class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None


# --- Session Create ---
class SessionCreate(SessionBase):
    parent_id: Optional[int] = None
    criteria: Optional[List[CriterionWithWeightCreate]] = []


# --- Session Update ---
class SessionUpdate(SessionBase):
    parent_id: Optional[int] = None
    criteria: Optional[List[CriterionWithWeightCreate]] = None


# --- Session Read ---
class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    parent_id: Optional[int] = None
    criteria: List[CriterionWithWeightRead] = []
    children: List["SessionRead"] = []

    class Config:
        orm_mode = True


# Required for self-referencing models
SessionRead.model_rebuild()
