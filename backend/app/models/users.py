from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func
)
from ..db import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
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
    criteria = relationship("UserCriterion", back_populates="user")

# --- Association table between User and Criterion ---
class UserCriterion(Base):
    __tablename__ = "user_criteria"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    phase_id = Column(Integer, ForeignKey("phases.id"), nullable=True)

    # For COUNTABLE type: store an integer
    count_value = Column(Integer, nullable=False, default=0)

    # For BOOLEAN type: store whether the criterion is fulfilled
    is_fulfilled = Column(Boolean, nullable=False, default=False)

    # For TEXT type
    text_value = Column(String, nullable=True)
    

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
    phase = relationship("Phase", back_populates="user_criteria")

