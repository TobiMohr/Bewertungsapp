from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List
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
    role_id: int
    weight: int

    class Config:
        orm_mode = True


class CriterionWithWeightCreate(BaseModel):
    id: int
    role_id: int
    weight: int = 1


# ---------- UserCriterion ----------
class UserCriterionTextRead(BaseModel):
    text_value: str
    is_active: bool
    created_at: str

    class Config:
        orm_mode = True


class UserCriterionBase(BaseModel):
    user_id: int
    criterion_id: int
    session_id: int

    @property
    def active_text(self):
        active = next((t.text_value for t in self.text_values if t.is_active), None)
        return active

    @property
    def last_texts(self):
        # last 5 inactive texts
        inactive = [t.text_value for t in self.text_values if not t.is_active]
        return inactive[:5]


class UserCriterionRead(UserCriterionBase):
    id: int
    count_value: Optional[int] = None
    is_fulfilled: Optional[bool] = None
    text_value: Optional[str] = None
    criterion: Optional[CriterionRead] = None
    user: Optional[UserRead] = None
    active_text: Optional[str] = None
    last_texts: Optional[List[str]] = []

    class Config:
        orm_mode = True

class UserCriterionUpdate(BaseModel):
    value: Optional[Union[str, bool, int]] = None
