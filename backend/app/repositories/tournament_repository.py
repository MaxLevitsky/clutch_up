# Feature: F001
# Scenario: SC001, SC002
# Tournament Repository

from sqlalchemy.orm import Session
from app.models.tournament import Tournament, TournamentStatus
from app.models.tournament_registration import TournamentRegistration
from typing import List, Optional


class TournamentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tournament_id: int) -> Optional[Tournament]:
        return self.db.query(Tournament).filter(Tournament.id == tournament_id).first()

    def get_eligible_tournaments(self, rank: str, region: str) -> List[Tournament]:
        return (
            self.db.query(Tournament)
            .filter(
                Tournament.rank_tier == rank,
                Tournament.region == region,
                Tournament.status == TournamentStatus.REGISTRATION_OPEN,
                Tournament.registered_count < Tournament.capacity
            )
            .all()
        )

    def register_player(self, tournament_id: int, player_id: int, team_id: Optional[int] = None) -> TournamentRegistration:
        registration = TournamentRegistration(
            tournament_id=tournament_id,
            player_id=player_id,
            team_id=team_id
        )
        self.db.add(registration)

        # Update registered count
        tournament = self.get_by_id(tournament_id)
        if tournament:
            tournament.registered_count += 1

        self.db.commit()
        self.db.refresh(registration)
        return registration

    def is_player_registered(self, tournament_id: int, player_id: int) -> bool:
        return (
            self.db.query(TournamentRegistration)
            .filter(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.player_id == player_id
            )
            .first() is not None
        )

    def get_all_tournaments(self) -> List[Tournament]:
        return self.db.query(Tournament).all()
