from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
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

    # Relationships
    users = relationship("UserCriterion", back_populates="criterion")
    phases = relationship(
        "Phase", secondary="phase_criteria_association", back_populates="criteria"
    )
    phase_criteria_assoc = relationship(
        "PhaseCriterion", back_populates="criterion", cascade="all, delete-orphan"
    )


