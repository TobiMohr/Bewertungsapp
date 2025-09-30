# schemas/sessions.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .criterias import CriterionWithWeightCreate
from .phases import PhaseRead, PhaseCreate

# --- Session Base ---
class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None

# --- Session Create ---
class SessionCreate(SessionBase):
    phases: Optional[List[PhaseCreate]] = []

# --- Session Update ---
class SessionUpdate(SessionBase):
    criteria: Optional[List[CriterionWithWeightCreate]] = []

# --- Session Read ---
class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    phases: List[PhaseRead] = []

    class Config:
        orm_mode = True 
