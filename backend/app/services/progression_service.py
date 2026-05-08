# Feature: F003
# Scenario: SC005
# Requirement: FR-11, FR-12

from sqlalchemy.orm import Session
from app.repositories.progression_repository import ProgressionRepository
from app.models.badge import Badge

BADGE_FIRST_STEPS = 1
BADGE_TEAM_PLAYER = 2
BADGE_MATCH_VICTOR = 3
BADGE_CHAMPION = 4
BADGE_VETERAN = 5

POINTS_PARTICIPATION = 10
POINTS_MATCH_WIN = 25
POINTS_RUNNER_UP = 50
POINTS_CHAMPION = 100


class ProgressionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProgressionRepository(db)

    def award_tournament_participation(self, player_id: int):
        self.repo.update_points(player_id, POINTS_PARTICIPATION)
        # add_badge is idempotent — First Steps is awarded on the first call
        self.repo.add_badge(player_id, BADGE_FIRST_STEPS)
        tournament_count = self.repo.get_tournament_count(player_id)
        if tournament_count >= 10:
            self.repo.add_badge(player_id, BADGE_VETERAN)

    def award_match_win(self, player_id: int):
        self.repo.update_points(player_id, POINTS_MATCH_WIN)
        match_wins = self.repo.get_match_win_count(player_id)
        if match_wins >= 1:
            self.repo.add_badge(player_id, BADGE_MATCH_VICTOR)

    def award_tournament_placement(self, player_id: int, placement: int):
        if placement == 1:
            self.repo.update_points(player_id, POINTS_CHAMPION)
            self.repo.add_badge(player_id, BADGE_CHAMPION)
        elif placement == 2:
            self.repo.update_points(player_id, POINTS_RUNNER_UP)

    def award_team_join(self, player_id: int):
        self.repo.add_badge(player_id, BADGE_TEAM_PLAYER)

    def get_player_progression(self, player_id: int) -> dict:
        prog = self.repo.get_by_player_id(player_id)
        badge_ids = [int(b) for b in prog.badges.split(",") if b]
        badges = self.db.query(Badge).filter(Badge.id.in_(badge_ids)).all() if badge_ids else []
        tournaments_played = self.repo.get_tournament_count(player_id)
        matches_won = self.repo.get_match_win_count(player_id)
        points_in_level = prog.points % 100

        return {
            "player_id": player_id,
            "points": prog.points,
            "level": prog.level,
            "badges": badges,
            "tournaments_played": tournaments_played,
            "matches_won": matches_won,
            "points_to_next_level": 100 - points_in_level if prog.level < 50 else 0,
        }
