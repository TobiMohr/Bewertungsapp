from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
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

class UserSessionRole(Base):
    __tablename__ = "user_session_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    created_at = Column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at = Column(
        String, default=lambda: datetime.now(timezone.utc).isoformat(),
        onupdate=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    user = relationship("User", backref="session_roles")
    session = relationship("Session", backref="user_roles")
    role = relationship("Role", back_populates="user_sessions")

