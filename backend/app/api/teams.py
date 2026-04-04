# Feature: F002
# Scenario: SC003, SC004
# Team API Endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.team_service import TeamService
from app.repositories.team_repository import TeamRepository
from app.repositories.player_repository import PlayerRepository
from app.repositories.tournament_repository import TournamentRepository
from app.schemas.team import TeamCreate, TeamResponse, TeamInviteCreate, TeamInviteResponse

router = APIRouter(prefix="/api/teams", tags=["teams"])


def get_team_service(db: Session = Depends(get_db)) -> TeamService:
    team_repo = TeamRepository(db)
    player_repo = PlayerRepository(db)
    tournament_repo = TournamentRepository(db)
    return TeamService(team_repo, player_repo, tournament_repo)


@router.post("/")
def create_team(
    team_data: TeamCreate,
    owner_id: int,
    service: TeamService = Depends(get_team_service)
):
    """
    Feature: F002
    Scenario: SC003
    Requirement: FR-6
    Create a new team with unique name
    """
    result = service.create_team(team_data.name, owner_id, team_data.badge)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    # Convert Team model to dict for JSON serialization
    if "team" in result and result["team"]:
        team = result["team"]
        result["team"] = {
            "id": team.id,
            "name": team.name,
            "badge": team.badge,
            "owner_id": team.owner_id,
            "created_at": team.created_at.isoformat() if team.created_at else None
        }

    return result


@router.post("/invites", response_model=dict)
def create_team_invite(
    invite_data: TeamInviteCreate,
    owner_id: int,
    service: TeamService = Depends(get_team_service)
):
    """
    Feature: F002
    Scenario: SC003
    Requirement: FR-7
    Generate shareable team invite link
    """
    result = service.create_invite(invite_data.team_id, owner_id)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/invites/{token}/accept", response_model=dict)
def accept_team_invite(
    token: str,
    player_id: int,
    service: TeamService = Depends(get_team_service)
):
    """
    Feature: F002
    Scenario: SC003
    Requirement: FR-7
    Accept team invite and join roster
    """
    result = service.accept_invite(token, player_id)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/{team_id}/roster", response_model=dict)
def get_team_roster(
    team_id: int,
    service: TeamService = Depends(get_team_service)
):
    """
    Feature: F002
    Scenario: SC003
    Requirement: FR-8
    Display current roster status and pending invites
    """
    result = service.get_team_roster(team_id)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@router.post("/{team_id}/register-tournament/{tournament_id}", response_model=dict)
def register_team_for_tournament(
    team_id: int,
    tournament_id: int,
    owner_id: int,
    service: TeamService = Depends(get_team_service)
):
    """
    Feature: F002
    Scenario: SC004
    Requirement: FR-9, FR-10
    Register team for tournament and lock roster
    """
    result = service.register_team_for_tournament(team_id, tournament_id, owner_id)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.delete("/invites/{token}/revoke", response_model=dict)
def revoke_team_invite(
    token: str,
    owner_id: int,
    service: TeamService = Depends(get_team_service)
):
    """
    Feature: F002
    Requirement: NFR-7
    Revoke team invite link
    """
    result = service.revoke_invite(token, owner_id)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result
