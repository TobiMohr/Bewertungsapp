from sqlalchemy import Column, Integer, String
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..db import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
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
    phases = relationship("Phase", back_populates="session", cascade="all, delete-orphan")
