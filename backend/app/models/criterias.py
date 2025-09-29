from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Enum,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from ..db import Base


# --- Enum for the criterion type ---

class CriterionType(PyEnum):
    countable = "countable"
    boolean = "boolean"
    text = "text"


# --- Criterion table ---
class Criterion(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(CriterionType, name="criteriontype", native_enum=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("UserCriterion", back_populates="criterion")
    sessions = relationship("Session", secondary="session_criteria_association", back_populates="criteria")
    session_criteria_assoc = relationship("SessionCriterion", back_populates="criterion", cascade="all, delete-orphan")


# --- Association table between User and Criterion ---
class UserCriterion(Base):
    __tablename__ = "user_criteria"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    # For COUNTABLE type: store an integer
    count_value = Column(Integer, nullable=False, default=0)

    # For BOOLEAN type: store whether the criterion is fulfilled
    is_fulfilled = Column(Boolean, nullable=False, default=False)

    # For TEXT type
    text_value = Column(String, nullable=True)
    

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="criteria")
    criterion = relationship("Criterion", back_populates="users")
    session = relationship("Session", back_populates="user_criteria")

