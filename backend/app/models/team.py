# Feature: F002
# Scenario: SC003, SC004
# Team Model

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    badge = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
