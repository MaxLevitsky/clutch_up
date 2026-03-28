# Feature: F001, F002, F003
# Scenario: All Scenarios
# Player Schemas

from pydantic import BaseModel, EmailStr
from datetime import datetime


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
