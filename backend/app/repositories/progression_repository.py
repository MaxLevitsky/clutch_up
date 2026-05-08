# Feature: F003
# Scenario: SC005

from sqlalchemy.orm import Session
from app.models.progression import Progression
from app.models.tournament_registration import TournamentRegistration


class ProgressionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_player_id(self, player_id: int) -> Progression:
        prog = self.db.query(Progression).filter(Progression.player_id == player_id).first()
        if not prog:
            prog = Progression(player_id=player_id)
            self.db.add(prog)
            self.db.commit()
            self.db.refresh(prog)
        return prog

    def update_points(self, player_id: int, points_delta: int) -> Progression:
        prog = self.get_by_player_id(player_id)
        prog.points = max(0, prog.points + points_delta)
        prog.level = min(50, 1 + prog.points // 100)
        self.db.commit()
        self.db.refresh(prog)
        return prog

    def add_badge(self, player_id: int, badge_id: int) -> bool:
        prog = self.get_by_player_id(player_id)
        existing = [b for b in prog.badges.split(",") if b] if prog.badges else []
        if str(badge_id) in existing:
            return False
        existing.append(str(badge_id))
        prog.badges = ",".join(existing)
        self.db.commit()
        return True

    def has_badge(self, player_id: int, badge_id: int) -> bool:
        prog = self.get_by_player_id(player_id)
        existing = [b for b in prog.badges.split(",") if b] if prog.badges else []
        return str(badge_id) in existing

    def get_tournament_count(self, player_id: int) -> int:
        return self.db.query(TournamentRegistration).filter(
            TournamentRegistration.player_id == player_id
        ).count()

    def get_match_win_count(self, player_id: int) -> int:
        from app.models.match import Match, MatchStatus
        return self.db.query(Match).filter(
            Match.winner_id == player_id,
            Match.status == MatchStatus.COMPLETED
        ).count()
