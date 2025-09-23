from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None

class SessionCreate(SessionBase):
    criteria_ids: Optional[List[int]] = []

class SessionUpdate(SessionBase):
    criteria_ids: Optional[List[int]] = []

class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    criterion_ids: List[int] = []

    class Config:
        orm_mode = True
