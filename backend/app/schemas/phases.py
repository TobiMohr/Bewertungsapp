# schemas/phases.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .criterias import CriterionWithWeightRead, CriterionWithWeightCreate

# --- Phase Base ---
class PhaseBase(BaseModel):
    title: str
    order: Optional[int] = None

# --- Phase creation ---
class PhaseCreate(PhaseBase):
    criteria: Optional[List[CriterionWithWeightCreate]] = []

# --- Phase update ---
class PhaseUpdate(PhaseBase):
    criteria: Optional[List[CriterionWithWeightCreate]] = None

# --- Phase read ---
class PhaseRead(PhaseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    criteria: List[CriterionWithWeightRead] = []

    class Config:
        orm_mode = True