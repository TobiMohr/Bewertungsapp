from pydantic import BaseModel
from enum import Enum
from typing import Optional


# ---------- Enum ----------
class CriterionType(str, Enum):
    countable = "countable"
    boolean = "boolean"
    text = "text"


# ---------- Criterion ----------   
class CriterionBase(BaseModel):
    name: str
    type: CriterionType


class CriterionCreate(CriterionBase):
    name: str
    type: CriterionType


class CriterionRead(CriterionBase):
    id: int

    class Config:
        orm_mode = True


# ---------- UserCriterion ----------
class UserCriterionBase(BaseModel):
    user_id: int
    criterion_id: int
    session_id: int


class UserCriterionRead(UserCriterionBase):
    id: int
    count_value: Optional[int] = None
    is_fulfilled: Optional[bool] = None
    text_value: Optional[str] = None
    criterion: Optional[CriterionRead] = None

    class Config:
        orm_mode = True
