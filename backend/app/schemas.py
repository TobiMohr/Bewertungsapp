# schemas.py
from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True  # allows SQLAlchemy objects to be returned directly
