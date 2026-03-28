# Feature: F002
# Scenario: SC003, SC004
# Team Schemas

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TeamCreate(BaseModel):
    name: str
    badge: Optional[str] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    badge: Optional[str]
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TeamInviteCreate(BaseModel):
    team_id: int


class TeamInviteResponse(BaseModel):
    id: int
    team_id: int
    token: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
