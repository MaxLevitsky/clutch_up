# Feature: F003
# Scenario: SC005
# Progression Model

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Progression(Base):
    __tablename__ = "progressions"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), unique=True, nullable=False, index=True)
    points = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    badges = Column(String, default="", nullable=False)  # Comma-separated badge IDs
    unlocked_tiers = Column(String, default="BEGINNER", nullable=False)  # Comma-separated tiers
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
