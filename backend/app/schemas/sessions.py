from pydantic import BaseModel
from datetime import datetime

class SessionBase(BaseModel):
    title: str
    description: str | None = None

class SessionCreate(SessionBase):
    pass

class SessionUpdate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
