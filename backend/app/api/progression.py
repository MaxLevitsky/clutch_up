# Feature: F003
# Scenario: SC005
# Requirement: FR-11, FR-12

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.progression_service import ProgressionService
from app.models.badge import Badge
from app.schemas.progression import ProgressionResponse, BadgeResponse
from typing import List

router = APIRouter(prefix="/api/progression", tags=["progression"])


def get_progression_service(db: Session = Depends(get_db)) -> ProgressionService:
    return ProgressionService(db)


@router.get("/badges/", response_model=List[BadgeResponse])
def get_all_badges(db: Session = Depends(get_db)):
    """Return all available badges in the system."""
    return db.query(Badge).all()


@router.get("/{player_id}", response_model=ProgressionResponse)
def get_player_progression(
    player_id: int,
    service: ProgressionService = Depends(get_progression_service),
):
    """
    Feature: F003
    Scenario: SC005
    Requirement: FR-12
    Get player progression, level, points and earned badges.
    """
    data = service.get_player_progression(player_id)
    return ProgressionResponse(**data)
