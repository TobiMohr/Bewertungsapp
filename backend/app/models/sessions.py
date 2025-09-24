from sqlalchemy import Column, Integer, Table, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .session_criteria_association import session_criteria_association

from ..db import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_criteria = relationship("UserCriterion", back_populates="session")
    criteria = relationship(
        "Criterion",
        secondary=session_criteria_association,
        back_populates="sessions"
    )
