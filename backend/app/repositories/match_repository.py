# Feature: F003
# Scenario: SC005

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.match import Match, MatchStatus
from typing import List, Optional


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, match: Match) -> Match:
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_by_id(self, match_id: int) -> Optional[Match]:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def get_by_tournament(self, tournament_id: int) -> List[Match]:
        return self.db.query(Match).filter(Match.tournament_id == tournament_id).all()

    def update_result(self, match_id: int, winner_id: int, loser_id: int) -> Optional[Match]:
        match = self.get_by_id(match_id)
        if not match:
            return None
        match.winner_id = winner_id
        match.loser_id = loser_id
        match.status = MatchStatus.COMPLETED
        match.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_all_completed(self, tournament_id: int) -> List[Match]:
        return self.db.query(Match).filter(
            Match.tournament_id == tournament_id,
            Match.status == MatchStatus.COMPLETED
        ).all()

    def get_pending_count(self, tournament_id: int) -> int:
        return self.db.query(Match).filter(
            Match.tournament_id == tournament_id,
            Match.status != MatchStatus.COMPLETED,
            Match.status != MatchStatus.CANCELLED,
        ).count()

    def get_by_tournament_and_round(self, tournament_id: int, round_num: int) -> List[Match]:
        return self.db.query(Match).filter(
            Match.tournament_id == tournament_id,
            Match.round_number == round_num
        ).order_by(Match.id).all()

    def get_win_counts(self, tournament_id: int) -> dict:
        completed = self.get_all_completed(tournament_id)
        wins: dict = {}
        for m in completed:
            if m.winner_id:
                wins[m.winner_id] = wins.get(m.winner_id, 0) + 1
        return wins
