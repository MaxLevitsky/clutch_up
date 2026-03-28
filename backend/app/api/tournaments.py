# Feature: F001
# Scenario: SC001, SC002
# Tournament API Endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.tournament_service import TournamentService
from app.repositories.tournament_repository import TournamentRepository
from app.repositories.player_repository import PlayerRepository
from app.schemas.tournament import TournamentResponse, TournamentListResponse
from app.schemas.registration import RegistrationRequest, RegistrationResponse
from typing import List

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


def get_tournament_service(db: Session = Depends(get_db)) -> TournamentService:
    tournament_repo = TournamentRepository(db)
    player_repo = PlayerRepository(db)
    return TournamentService(tournament_repo, player_repo)


@router.get("/eligible/{player_id}", response_model=TournamentListResponse)
def get_eligible_tournaments(
    player_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """
    Feature: F001
    Scenario: SC001
    Requirement: FR-1
    Get tournaments eligible for a specific player based on rank and region
    """
    try:
        tournaments = service.get_eligible_tournaments(player_id)
        return TournamentListResponse(
            tournaments=tournaments,
            total=len(tournaments)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=TournamentListResponse)
def get_all_tournaments(
    service: TournamentService = Depends(get_tournament_service)
):
    """Get all tournaments"""
    tournaments = service.get_all_tournaments()
    return TournamentListResponse(
        tournaments=tournaments,
        total=len(tournaments)
    )


@router.post("/register", response_model=RegistrationResponse)
def register_for_tournament(
    request: RegistrationRequest,
    player_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """
    Feature: F001
    Scenario: SC001, SC002
    Requirement: FR-2, FR-3, FR-4, FR-5
    Register a player for a tournament with eligibility validation
    """
    result = service.register_player(player_id, request.tournament_id)

    if result["status"] == "error":
        return RegistrationResponse(
            status=result["status"],
            message=result["message"],
            tournament_id=result["tournament_id"],
            player_id=result["player_id"],
            eligibility=result.get("eligibility")
        )

    return RegistrationResponse(
        status=result["status"],
        message=result["message"],
        tournament_id=result["tournament_id"],
        player_id=result["player_id"],
        registered_at=result.get("registered_at")
    )


@router.get("/validate-eligibility/{player_id}/{tournament_id}")
def validate_tournament_eligibility(
    player_id: int,
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """
    Feature: F001
    Scenario: SC002
    Requirement: FR-4, FR-5
    Validate player eligibility for a tournament
    """
    return service.validate_eligibility(player_id, tournament_id)
