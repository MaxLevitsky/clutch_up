# Feature: F001
# Scenario: SC001, SC002
# Tournament Schemas

from pydantic import BaseModel
from datetime import datetime
from typing import List


class TournamentResponse(BaseModel):
    id: int
    name: str
    rank_tier: str
    region: str
    capacity: int
    registered_count: int
    status: str
    start_time: datetime
    format: str
    is_team_tournament: int
    team_size: int | None

    class Config:
        from_attributes = True


class TournamentListResponse(BaseModel):
    tournaments: List[TournamentResponse]
    total: int
