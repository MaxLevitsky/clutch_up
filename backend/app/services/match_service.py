# Feature: F003
# Scenario: SC005

import math
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.match import Match, MatchStatus
from app.models.tournament import Tournament, TournamentStatus
from app.models.tournament_registration import TournamentRegistration
from app.repositories.match_repository import MatchRepository
from app.services.progression_service import ProgressionService
from typing import List, Optional


class MatchService:
    def __init__(self, db: Session):
        self.db = db
        self.match_repo = MatchRepository(db)
        self.progression_service = ProgressionService(db)

    def create_match(
        self,
        tournament_id: int,
        player1_id: int,
        player2_id: int,
        round_number: int,
        scheduled_time: datetime,
    ) -> dict:
        tournament = self.db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return {"status": "error", "message": "Tournament not found"}
        if player1_id == player2_id:
            return {"status": "error", "message": "Players must be different"}

        match = Match(
            tournament_id=tournament_id,
            player1_id=player1_id,
            player2_id=player2_id,
            round_number=round_number,
            scheduled_time=scheduled_time,
            status=MatchStatus.SCHEDULED,
        )
        created = self.match_repo.create(match)
        return {"status": "success", "match": created}

    def record_result(self, match_id: int, winner_id: int, loser_id: int) -> dict:
        match = self.match_repo.get_by_id(match_id)
        if not match:
            return {"status": "error", "message": "Match not found"}
        if match.status == MatchStatus.COMPLETED:
            return {"status": "error", "message": "Match already completed"}

        updated = self.match_repo.update_result(match_id, winner_id, loser_id)
        self._advance_winner(match, winner_id)
        self.progression_service.award_match_win(winner_id)

        if self.match_repo.get_pending_count(match.tournament_id) == 0:
            self._finalize_tournament(match.tournament_id)

        return {"status": "success", "match": updated}

    def _advance_winner(self, match: Match, winner_id: int):
        round_matches = self.match_repo.get_by_tournament_and_round(
            match.tournament_id, match.round_number
        )
        next_round_matches = self.match_repo.get_by_tournament_and_round(
            match.tournament_id, match.round_number + 1
        )
        if not next_round_matches:
            return
        current_idx = next(i for i, m in enumerate(round_matches) if m.id == match.id)
        target = next_round_matches[current_idx // 2]
        if current_idx % 2 == 0:
            target.player1_id = winner_id
        else:
            target.player2_id = winner_id
        self.db.commit()

    def _finalize_tournament(self, tournament_id: int):
        tournament = self.db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            return

        win_counts = self.match_repo.get_win_counts(tournament_id)
        if not win_counts:
            return

        sorted_players = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_players:
            self.progression_service.award_tournament_placement(sorted_players[0][0], 1)
        if len(sorted_players) > 1:
            self.progression_service.award_tournament_placement(sorted_players[1][0], 2)

        tournament.status = TournamentStatus.COMPLETED
        self.db.commit()

    def get_tournament_matches(self, tournament_id: int) -> List[Match]:
        return self.match_repo.get_by_tournament(tournament_id)

    def generate_bracket(self, tournament_id: int, capacity: int, format: str, start_time: datetime):
        """Create match slots and assign registered players to first-round slots."""
        # Delete any previously generated empty slots (e.g. from a prior incomplete generation)
        self.db.query(Match).filter(
            Match.tournament_id == tournament_id,
            Match.status == MatchStatus.SCHEDULED,
            Match.player1_id.is_(None),
            Match.player2_id.is_(None),
        ).delete()
        self.db.commit()

        registrations = self.db.query(TournamentRegistration).filter(
            TournamentRegistration.tournament_id == tournament_id
        ).all()
        player_ids = [r.player_id for r in registrations]
        random.shuffle(player_ids)

        if format in ("Single Elimination", "Double Elimination"):
            slots = self._single_elim_slots(capacity)
            multiplier = 2 if format == "Double Elimination" else 1
            for _ in range(multiplier):
                for round_num, count in slots:
                    for _ in range(count):
                        match = Match(
                            tournament_id=tournament_id,
                            round_number=round_num,
                            scheduled_time=start_time + timedelta(days=round_num - 1),
                            status=MatchStatus.SCHEDULED,
                        )
                        self.db.add(match)
        elif format == "Round Robin":
            total = capacity * (capacity - 1) // 2
            for i in range(total):
                match = Match(
                    tournament_id=tournament_id,
                    round_number=1,
                    scheduled_time=start_time + timedelta(days=i),
                    status=MatchStatus.SCHEDULED,
                )
                self.db.add(match)
        self.db.commit()

        # Assign players to first-round slots
        if format in ("Single Elimination", "Double Elimination") and player_ids:
            first_round_matches = self.match_repo.get_by_tournament_and_round(tournament_id, 1)
            for i, match in enumerate(first_round_matches):
                p1_idx = i * 2
                p2_idx = i * 2 + 1
                if p1_idx < len(player_ids):
                    match.player1_id = player_ids[p1_idx]
                if p2_idx < len(player_ids):
                    match.player2_id = player_ids[p2_idx]
                else:
                    # Bye: auto-complete this match with player1 advancing
                    match.winner_id = player_ids[p1_idx]
                    match.loser_id = None
                    match.status = MatchStatus.COMPLETED
                    match.completed_at = datetime.utcnow()

        if player_ids:
            tournament = self.db.query(Tournament).filter(Tournament.id == tournament_id).first()
            if tournament:
                tournament.status = TournamentStatus.IN_PROGRESS
        self.db.commit()

        # Advance bye winners to the next round
        if format in ("Single Elimination", "Double Elimination") and player_ids:
            first_round_matches = self.match_repo.get_by_tournament_and_round(tournament_id, 1)
            for match in first_round_matches:
                if match.status == MatchStatus.COMPLETED and match.winner_id:
                    self._advance_winner(match, match.winner_id)

    @staticmethod
    def _single_elim_slots(capacity: int) -> List[tuple]:
        """Return [(round_number, match_count)] for a single elimination bracket."""
        slots = []
        remaining = max(capacity, 2)
        round_num = 1
        while remaining > 1:
            matches = remaining // 2
            slots.append((round_num, matches))
            remaining = (remaining + 1) // 2
            round_num += 1
        return slots
