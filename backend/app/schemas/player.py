# Feature: F001, F002, F003
# Scenario: All Scenarios
# Player Schemas

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


class PlayerCreate(BaseModel):
    username: str
    email: EmailStr
    region: str


class PlayerResponse(BaseModel):
    id: int
    username: str
    email: str
    rank: str
    region: str
    progression_level: int
    account_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BadgeSummary(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class PlayerProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    rank: str
    region: str
    account_status: str
    created_at: datetime
    points: int
    level: int
    badges: List[BadgeSummary]
    tournaments_played: int
    matches_won: int
    points_to_next_level: int

    class Config:
        from_attributes = True
