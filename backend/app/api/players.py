# Feature: F001, F002, F003
# Scenario: All Scenarios
# Player API Endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.player_service import PlayerService
from app.repositories.player_repository import PlayerRepository
from app.schemas.player import PlayerCreate, PlayerResponse

router = APIRouter(prefix="/api/players", tags=["players"])


def get_player_service(db: Session = Depends(get_db)) -> PlayerService:
    player_repo = PlayerRepository(db)
    return PlayerService(player_repo)


@router.post("/", response_model=PlayerResponse)
def create_player(
    player_data: PlayerCreate,
    service: PlayerService = Depends(get_player_service)
):
    """Create a new player account"""
    try:
        player = service.create_player(
            player_data.username,
            player_data.email,
            player_data.region
        )
        return player
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: int,
    service: PlayerService = Depends(get_player_service)
):
    """Get player by ID"""
    player = service.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
