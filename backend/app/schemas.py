# schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: str
    last_name:str
    email: EmailStr

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True  # allows SQLAlchemy objects to be returned directly

class UserLogin(BaseModel):
    email: EmailStr
    password: str