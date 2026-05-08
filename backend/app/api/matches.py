# Feature: F003
# Scenario: SC005

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.match_service import MatchService
from app.schemas.match import MatchCreateRequest, MatchResultRequest, MatchResponse
from app.models.player import Player
from app.models.tournament import Tournament
from app.dependencies import get_current_player_id
from typing import List

router = APIRouter(prefix="/api/matches", tags=["matches"])


def get_match_service(db: Session = Depends(get_db)) -> MatchService:
    return MatchService(db)


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(request: MatchCreateRequest, service: MatchService = Depends(get_match_service)):
    """Create a scheduled match between two players in a tournament."""
    result = service.create_match(
        tournament_id=request.tournament_id,
        player1_id=request.player1_id,
        player2_id=request.player2_id,
        round_number=request.round_number,
        scheduled_time=request.scheduled_time,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return result["match"]


@router.get("/tournament/{tournament_id}", response_model=List[MatchResponse])
def get_tournament_matches(
    tournament_id: int,
    service: MatchService = Depends(get_match_service),
    db: Session = Depends(get_db),
):
    """Get all matches for a tournament, with player usernames resolved."""
    matches = service.get_tournament_matches(tournament_id)
    player_ids = set()
    for m in matches:
        for pid in (m.player1_id, m.player2_id, m.winner_id):
            if pid:
                player_ids.add(pid)
    players = {p.id: p.username for p in db.query(Player).filter(Player.id.in_(player_ids)).all()}
    result = []
    for m in matches:
        d = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        d["player1_username"] = players.get(m.player1_id)
        d["player2_username"] = players.get(m.player2_id)
        d["winner_username"] = players.get(m.winner_id)
        result.append(d)
    return result


@router.post("/{match_id}/result", response_model=MatchResponse)
def record_result(
    match_id: int,
    request: MatchResultRequest,
    service: MatchService = Depends(get_match_service),
    db: Session = Depends(get_db),
    current_player_id: int = Depends(get_current_player_id),
):
    """
    Feature: F003
    Scenario: SC005
    Record match result and trigger progression awards.
    """
    match = service.match_repo.get_by_id(match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    tournament = db.query(Tournament).filter(Tournament.id == match.tournament_id).first()
    if tournament and tournament.creator_id is not None and tournament.creator_id != current_player_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the tournament creator can record results")
    result = service.record_result(match_id, request.winner_id, request.loser_id)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return result["match"]
