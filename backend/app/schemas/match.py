# Feature: F003
# Scenario: SC005

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MatchCreateRequest(BaseModel):
    tournament_id: int
    player1_id: int
    player2_id: int
    round_number: int = 1
    scheduled_time: datetime


class MatchResultRequest(BaseModel):
    winner_id: int
    loser_id: int


class MatchResponse(BaseModel):
    id: int
    tournament_id: int
    status: str
    round_number: int
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None
    winner_id: Optional[int] = None
    loser_id: Optional[int] = None
    player1_username: Optional[str] = None
    player2_username: Optional[str] = None
    winner_username: Optional[str] = None
    scheduled_time: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
