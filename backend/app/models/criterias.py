from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
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
    created_at = Column(
        String, 
        default=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at = Column(
        String, 
        default=lambda: datetime.now(timezone.utc).isoformat(),
        onupdate=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    users = relationship("UserCriterion", back_populates="criterion")
    sessions = relationship(
        "Session", secondary="session_criteria_association", back_populates="criteria"
    )
    session_criteria_assoc = relationship(
        "SessionCriterion", back_populates="criterion", cascade="all, delete-orphan"
    )


