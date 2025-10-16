from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..db import Base

class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="Gesamtsession")
    description = Column(String, nullable=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("phases.id"), nullable=True)

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
    session = relationship("Session", back_populates="phases")

    parent = relationship(
        "Phase",
        remote_side=[id],
        back_populates="children"
    )
    children = relationship(
        "Phase",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    # Other existing relationships
    criteria = relationship(
        "Criterion", secondary="phase_criteria_association", back_populates="phases"
    )
    phase_criteria_assoc = relationship(
        "PhaseCriterion", back_populates="phase", cascade="all, delete-orphan"
    )
    user_criteria = relationship(
        "UserCriterion", back_populates="phase", cascade="all, delete-orphan"
    )

# --- Association table between Phase and Criterion ---
class PhaseCriterion(Base):
    __tablename__ = "phase_criteria_association"

    phase_id = Column(Integer, ForeignKey("phases.id"), primary_key=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), primary_key=True)
    weight = Column(Integer, nullable=False, default=1)

    # Relationships
    phase = relationship("Phase", back_populates="phase_criteria_assoc")
    criterion = relationship("Criterion", back_populates="phase_criteria_assoc")