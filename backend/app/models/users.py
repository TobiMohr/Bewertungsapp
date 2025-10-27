from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Index
)
from ..db import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

# --- User table ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
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
    team = relationship("Team", back_populates="users")
    criteria = relationship("UserCriterion", back_populates="user")
    session_comments = relationship("UserSessionComment", back_populates="user", cascade="all, delete-orphan")

# --- Team table ---
class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(
        String, 
        default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    users = relationship("User", back_populates="team")


# --- Association table between User and Criterion ---
class UserCriterion(Base):
    __tablename__ = "user_criteria"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

    # For COUNTABLE type: store an integer
    count_value = Column(Integer, nullable=False, default=0)

    # For BOOLEAN type: store whether the criterion is fulfilled
    is_fulfilled = Column(Boolean, nullable=False, default=False)

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
    user = relationship("User", back_populates="criteria")
    criterion = relationship("Criterion", back_populates="users")
    session = relationship("Session", back_populates="user_criteria")

    text_values = relationship(
        "UserCriterionText",
        back_populates="user_criterion",
        cascade="all, delete-orphan",
        order_by="desc(UserCriterionText.created_at)"
    )

    @property
    def active_text(self):
        """Return the currently active text value, or None if none active."""
        for t in self.text_values:
            if t.is_active:
                return t.text_value
        return None


# --- Table for storing multiple text values per UserCriterion ---
class UserCriterionText(Base):
    __tablename__ = "user_criterion_texts"

    id = Column(Integer, primary_key=True, index=True)
    user_criterion_id = Column(Integer, ForeignKey("user_criteria.id"), nullable=False)
    text_value = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)  # mark if this is current
    created_at = Column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationship
    user_criterion = relationship("UserCriterion", back_populates="text_values")

    # Index to speed up queries for active texts
    __table_args__ = (
        Index('idx_user_criterion_active', 'user_criterion_id', 'is_active'),
    )
