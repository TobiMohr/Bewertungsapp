from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from ..db import Base

class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="Gesamtsession")
    description = Column(String, nullable=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    session = relationship("Session", back_populates="phases")

    # Relationships
    criteria = relationship(
        "Criterion", secondary="phase_criteria_association", back_populates="phases"
    )
    phase_criteria_assoc = relationship(
        "PhaseCriterion", back_populates="phase", cascade="all, delete-orphan"
    )
    user_criteria = relationship("UserCriterion", back_populates="phase", cascade="all, delete-orphan")

# --- Association table between Phase and Criterion ---
class PhaseCriterion(Base):
    __tablename__ = "phase_criteria_association"

    phase_id = Column(Integer, ForeignKey("phases.id"), primary_key=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), primary_key=True)
    weight = Column(Integer, nullable=False, default=1)

    # Relationships
    phase = relationship("Phase", back_populates="phase_criteria_assoc")
    criterion = relationship("Criterion", back_populates="phase_criteria_assoc")