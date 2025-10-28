from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(String, nullable=True)
    message_id = Column(String, nullable=True, unique=True)
    channel_id = Column(String, nullable=True)
    sent_at = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    roles = Column(String, nullable=True)
    category = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(
        String,
        default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    user = relationship("User", back_populates="messages")
    criteria_ratings = relationship("MessageCriterion", back_populates="message", cascade="all, delete-orphan")


# --- Association table between Message and Criterion (rating per message) ---
class MessageCriterion(Base):
    __tablename__ = "message_criteria"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    reviewed = Column(Boolean, default=False, nullable=False)

    # Bewertung je nach Typ
    count_value = Column(Integer, nullable=True)
    is_fulfilled = Column(Boolean, nullable=True)
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
    message = relationship("Message", back_populates="criteria_ratings")
    criterion = relationship("Criterion")
