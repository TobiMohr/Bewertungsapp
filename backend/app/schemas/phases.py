# schemas/phases.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .criterias import CriterionWithWeightRead, CriterionWithWeightCreate

# --- Phase Base ---
class PhaseBase(BaseModel):
    title: str
    description: Optional[str] = None

# --- Phase creation ---
class PhaseCreate(PhaseBase):
    session_id: Optional[int] = None
    parent_id: Optional[int] = None
    criteria: Optional[List[CriterionWithWeightCreate]] = []

# --- Phase update ---
class PhaseUpdate(PhaseBase):
    criteria: Optional[List[CriterionWithWeightCreate]] = None
    parent_id: Optional[int] = None

# --- Phase read ---
class PhaseRead(PhaseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    session_id: Optional[int]
    parent_id: Optional[int]
    criteria: List[CriterionWithWeightRead] = []
    children: List["PhaseRead"] = []

    class Config:
        orm_mode = True

# Required for self-referencing models
PhaseRead.model_rebuild()
