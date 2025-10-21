from sqlalchemy import Column, Integer, String, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..db import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

    created_at = Column(
        String,
        default=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at = Column(
        String,
        default=lambda: datetime.now(timezone.utc).isoformat(),
        onupdate=lambda: datetime.now(timezone.utc).isoformat()
    )

    # --- Self-relationship for hierarchy ---
    parent = relationship(
        "Session",
        remote_side=[id],
        back_populates="children"
    )
    children = relationship(
        "Session",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    # --- Relationships with criteria ---
    criteria = relationship(
        "Criterion",
        secondary="session_criteria_association",
        back_populates="sessions"
    )
    session_criteria_assoc = relationship(
        "SessionCriterion",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    user_criteria = relationship(
        "UserCriterion",
        back_populates="session",
        cascade="all, delete-orphan"
    )

# --- Association table between Session and Criterion ---
class SessionCriterion(Base):
    __tablename__ = "session_criteria_association"

    session_id = Column(Integer, ForeignKey("sessions.id"), primary_key=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), primary_key=True)
    weight = Column(Integer, nullable=False, default=1)

    session = relationship("Session", back_populates="session_criteria_assoc")
    criterion = relationship("Criterion", back_populates="session_criteria_assoc")
