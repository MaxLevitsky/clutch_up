# Feature: F001
# Scenario: SC001, SC002
# Tournament Model

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TournamentStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    REGISTRATION_CLOSED = "REGISTRATION_CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rank_tier = Column(String, nullable=False)
    region = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    registered_count = Column(Integer, default=0, nullable=False)
    status = Column(Enum(TournamentStatus), default=TournamentStatus.UPCOMING, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    format = Column(String, nullable=False)
    is_team_tournament = Column(Integer, default=0, nullable=False)  # 0 = solo, 1 = team
    team_size = Column(Integer, nullable=True)
    creator_id = Column(Integer, ForeignKey("players.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("Player", foreign_keys=[creator_id], lazy="joined")

    @property
    def creator_username(self):
        return self.creator.username if self.creator else None
