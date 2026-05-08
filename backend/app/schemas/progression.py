# Feature: F003
# Scenario: SC005

from pydantic import BaseModel
from typing import List, Optional


class BadgeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProgressionResponse(BaseModel):
    player_id: int
    points: int
    level: int
    badges: List[BadgeResponse]
    tournaments_played: int
    matches_won: int
    points_to_next_level: int

    class Config:
        from_attributes = True
