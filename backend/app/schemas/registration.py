# Feature: F001
# Scenario: SC001, SC002
# Registration Schemas

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RegistrationRequest(BaseModel):
    tournament_id: int
    team_id: Optional[int] = None


class RegistrationResponse(BaseModel):
    status: str
    message: str
    tournament_id: int
    player_id: int
    registered_at: Optional[datetime] = None
    eligibility: Optional[dict] = None

    class Config:
        from_attributes = True
