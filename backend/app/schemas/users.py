# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from .teams import TeamRead

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    team_id: Optional[int] = None
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: str
    last_name:str
    team_id: Optional[int] = None
    email: EmailStr

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    team_id: Optional[TeamRead] = None
    email: EmailStr

    class Config:
        orm_mode = True  # allows SQLAlchemy objects to be returned directly

class UserLogin(BaseModel):
    email: EmailStr
    password: str