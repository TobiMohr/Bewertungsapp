from pydantic import BaseModel, EmailStr

# --- Team Schemas ---
class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int
    created_at: str

    class Config:
        orm_mode = True