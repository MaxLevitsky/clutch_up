# Feature: F001, F004
# Scenario: SC001, SC002, SC007
# Tournament Schemas

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


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
    creator_id: Optional[int] = None
    creator_username: Optional[str] = None

    class Config:
        from_attributes = True


class TournamentListResponse(BaseModel):
    tournaments: List[TournamentResponse]
    total: int


# Feature: F004
# Scenario: SC007
# Requirements: FR-13, FR-14, FR-16
class TournamentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    rank_tier: str = Field(..., pattern="^(BEGINNER|INTERMEDIATE|ADVANCED|EXPERT)$")
    region: str = Field(..., pattern="^(NA|EU|ASIA)$")
    capacity: int = Field(..., ge=1, le=64)
    format: str = Field(..., min_length=1, max_length=100)
    start_time: datetime
    is_team_tournament: bool
    team_size: Optional[int] = Field(None, ge=2, le=5)


class TournamentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    rank_tier: Optional[str] = Field(None, pattern="^(BEGINNER|INTERMEDIATE|ADVANCED|EXPERT)$")
    region: Optional[str] = Field(None, pattern="^(NA|EU|ASIA)$")
    capacity: Optional[int] = Field(None, ge=1, le=64)
    format: Optional[str] = Field(None, min_length=1, max_length=100)
    start_time: Optional[datetime] = None
