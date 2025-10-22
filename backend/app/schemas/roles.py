from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class RoleAssignRequest(BaseModel):
    role_id: int
