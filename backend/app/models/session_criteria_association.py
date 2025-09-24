from sqlalchemy import Column, Integer, Table, ForeignKey

from ..db import Base


# Zwischentabelle für vorgeschlagene Kriterien
session_criteria_association = Table(
    "session_criteria_association",
    Base.metadata,
    Column("session_id", Integer, ForeignKey("sessions.id"), primary_key=True),
    Column("criterion_id", Integer, ForeignKey("criteria.id"), primary_key=True),
)