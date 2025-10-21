from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union
from .users import UserRead


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

class CriterionWithWeightRead(BaseModel):
    criterion: CriterionRead
    weight: int

    class Config:
        orm_mode = True


class CriterionWithWeightCreate(BaseModel):
    id: int
    weight: int = 1


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
    user: Optional[UserRead] = None

    class Config:
        orm_mode = True

class UserCriterionUpdate(BaseModel):
    value: Optional[Union[str, bool, int]] = None
