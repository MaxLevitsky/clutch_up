# Feature: F001, F004
# Scenario: SC001, SC002, SC007
# Tournament API Endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.tournament_service import TournamentService
from app.services.progression_service import ProgressionService
from app.services.match_service import MatchService
from app.repositories.tournament_repository import TournamentRepository
from app.repositories.player_repository import PlayerRepository
from app.schemas.tournament import TournamentResponse, TournamentListResponse, TournamentCreateRequest, TournamentUpdateRequest
from app.dependencies import get_current_player_id
from app.schemas.registration import RegistrationRequest, RegistrationResponse
from typing import List
from pydantic import ValidationError

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


def get_tournament_service(db: Session = Depends(get_db)) -> TournamentService:
    tournament_repo = TournamentRepository(db)
    player_repo = PlayerRepository(db)
    progression_service = ProgressionService(db)
    return TournamentService(tournament_repo, player_repo, progression_service)


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


@router.get("/{tournament_id}", response_model=TournamentResponse)
def get_tournament(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service)
):
    """Get a single tournament by ID."""
    tournament = service.tournament_repo.get_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.put("/{tournament_id}", response_model=TournamentResponse)
def update_tournament(
    tournament_id: int,
    request: TournamentUpdateRequest,
    current_player_id: int = Depends(get_current_player_id),
    service: TournamentService = Depends(get_tournament_service),
):
    """Update tournament parameters. Only the creator can edit."""
    update_data = request.model_dump(exclude_unset=True)
    result = service.update_tournament(tournament_id, update_data, current_player_id)

    if result["status"] == "error":
        code = result.get("code", 400)
        raise HTTPException(status_code=code, detail=result["message"])

    return result["tournament"]


@router.post("/{tournament_id}/generate-bracket")
def generate_bracket(
    tournament_id: int,
    service: TournamentService = Depends(get_tournament_service),
    db: Session = Depends(get_db),
):
    """Generate (or regenerate) the bracket for a tournament."""
    tournament = service.tournament_repo.get_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    from app.models.match import Match
    db.query(Match).filter(Match.tournament_id == tournament_id).delete()
    db.commit()
    MatchService(db).generate_bracket(
        tournament_id=tournament_id,
        capacity=tournament.capacity,
        format=tournament.format,
        start_time=tournament.start_time,
    )
    return {"status": "success", "message": "Bracket generated"}


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


@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
def create_tournament(
    request: TournamentCreateRequest,
    current_player_id: int = Depends(get_current_player_id),
    service: TournamentService = Depends(get_tournament_service),
    db: Session = Depends(get_db),
):
    """
    Feature: F004
    Scenario: SC007
    Requirements: FR-13, FR-14, FR-15, FR-16
    NFR: NFR-12, NFR-13, NFR-14
    Create a new tournament
    """
    try:
        result = service.create_tournament(
            name=request.name,
            rank_tier=request.rank_tier,
            region=request.region,
            capacity=request.capacity,
            format=request.format,
            start_time=request.start_time,
            is_team_tournament=request.is_team_tournament,
            team_size=request.team_size,
            creator_id=current_player_id,
        )

        # NFR-13: Return 400 with clear error messages for validation errors
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        tournament = result["tournament"]
        # NFR-14: Return 201 Created, tournament immediately visible via GET /api/tournaments/
        return tournament

    except ValidationError as e:
        # NFR-13: Pydantic validation errors return 400 with clear messages
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
