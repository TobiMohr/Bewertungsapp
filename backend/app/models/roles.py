from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..db import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

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
    user_sessions = relationship("UserSessionRole", back_populates="role")
    session_criteria = relationship("SessionCriterion", back_populates="role")

