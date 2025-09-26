from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class SessionCriterion(Base):
    __tablename__ = "session_criteria_association"

    session_id = Column(Integer, ForeignKey("sessions.id"), primary_key=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), primary_key=True)
    weight = Column(Integer, nullable=False, default=1)

    session = relationship("Session", back_populates="session_criteria_assoc")
    criterion = relationship("Criterion", back_populates="session_criteria_assoc")
