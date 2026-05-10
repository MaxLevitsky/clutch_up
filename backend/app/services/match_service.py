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

        tournament = self.db.query(Tournament).filter(Tournament.id == match.tournament_id).first()

        if tournament and tournament.format == "Double Elimination":
            wb_rounds = math.ceil(math.log2(max(tournament.capacity, 2)))
            if match.round_number == 200:
                pass  # GF done — finalize handled below
            elif match.round_number <= wb_rounds:
                self._advance_wb_winner(match, winner_id, wb_rounds)
                self._route_loser_to_lb(match, loser_id)
            else:
                self._advance_lb_winner(match, winner_id, wb_rounds)
        else:
            self._advance_winner(match, winner_id)

        self.progression_service.award_match_win(winner_id)

        if self.match_repo.get_pending_count(match.tournament_id) == 0:
            self._finalize_tournament(match.tournament_id)

        return {"status": "success", "match": updated}

    # ── Single Elimination advancement ────────────────────────────────────────

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
        target_idx = current_idx // 2
        if target_idx >= len(next_round_matches):
            return
        target = next_round_matches[target_idx]
        if current_idx % 2 == 0:
            target.player1_id = winner_id
        else:
            target.player2_id = winner_id
        self.db.commit()

    # ── Double Elimination advancement ────────────────────────────────────────

    def _advance_wb_winner(self, match: Match, winner_id: int, wb_rounds: int):
        """WB winner advances to next WB round, or to GF if WB Final."""
        if match.round_number < wb_rounds:
            self._advance_winner(match, winner_id)
        else:
            # WB Final winner → GF player1 slot
            self._fill_slot(match.tournament_id, 200, winner_id)

    def _route_loser_to_lb(self, match: Match, loser_id: int):
        """Drop a WB loser into the correct LB round."""
        r = match.round_number
        lb_round = 101 if r == 1 else 100 + 2 * (r - 1)
        self._fill_slot(match.tournament_id, lb_round, loser_id)

    def _advance_lb_winner(self, match: Match, winner_id: int, wb_rounds: int):
        """LB winner advances to next LB round, or to GF if LB Final."""
        max_lb_round = 100 + 2 * (wb_rounds - 1)
        if match.round_number == max_lb_round:
            # LB Final winner → GF player2 slot
            self._fill_slot(match.tournament_id, 200, winner_id)
        else:
            self._fill_slot(match.tournament_id, match.round_number + 1, winner_id)

    def _fill_slot(self, tournament_id: int, round_num: int, player_id: int):
        """Place player_id into the first empty slot of the given round."""
        matches = self.match_repo.get_by_tournament_and_round(tournament_id, round_num)
        for m in matches:
            if m.player1_id is None:
                m.player1_id = player_id
                self.db.commit()
                return
            if m.player2_id is None:
                m.player2_id = player_id
                self.db.commit()
                return

    # ── Tournament finalization ───────────────────────────────────────────────

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

    # ── Bracket generation ────────────────────────────────────────────────────

    def generate_bracket(self, tournament_id: int, capacity: int, format: str, start_time: datetime):
        """Create match slots and assign registered players to first-round slots."""
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

        if format == "Single Elimination":
            slots = self._single_elim_slots(capacity)
        elif format == "Double Elimination":
            slots = self._double_elim_slots(capacity)
        elif format == "Round Robin":
            total = capacity * (capacity - 1) // 2
            slots = [(1, total)]
        else:
            slots = self._single_elim_slots(capacity)

        for round_num, count in slots:
            if format == "Round Robin":
                # Round robin: create all matches in round 1 with sequential day offsets
                for i in range(count):
                    match = Match(
                        tournament_id=tournament_id,
                        round_number=1,
                        scheduled_time=start_time + timedelta(days=i),
                        status=MatchStatus.SCHEDULED,
                    )
                    self.db.add(match)
            else:
                for _ in range(count):
                    match = Match(
                        tournament_id=tournament_id,
                        round_number=round_num,
                        scheduled_time=start_time + timedelta(days=round_num - 1),
                        status=MatchStatus.SCHEDULED,
                    )
                    self.db.add(match)
        self.db.commit()

        # Assign players to first-round (WB R1) slots
        if format in ("Single Elimination", "Double Elimination") and player_ids:
            first_round_matches = self.match_repo.get_by_tournament_and_round(tournament_id, 1)
            for i, match in enumerate(first_round_matches):
                p1_idx = i * 2
                p2_idx = i * 2 + 1
                if p1_idx < len(player_ids):
                    match.player1_id = player_ids[p1_idx]
                if p2_idx < len(player_ids):
                    match.player2_id = player_ids[p2_idx]
                elif p1_idx < len(player_ids):
                    # Bye: only player1, auto-advance
                    match.winner_id = player_ids[p1_idx]
                    match.loser_id = None
                    match.status = MatchStatus.COMPLETED
                    match.completed_at = datetime.utcnow()

        if player_ids:
            tournament = self.db.query(Tournament).filter(Tournament.id == tournament_id).first()
            if tournament:
                tournament.status = TournamentStatus.IN_PROGRESS
        self.db.commit()

        # Advance bye winners
        if format in ("Single Elimination", "Double Elimination") and player_ids:
            first_round_matches = self.match_repo.get_by_tournament_and_round(tournament_id, 1)
            for match in first_round_matches:
                if match.status == MatchStatus.COMPLETED and match.winner_id:
                    if format == "Double Elimination":
                        wb_rounds = math.ceil(math.log2(max(capacity, 2)))
                        self._advance_wb_winner(match, match.winner_id, wb_rounds)
                        # No loser for a bye
                    else:
                        self._advance_winner(match, match.winner_id)

    # ── Slot helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _next_power_of_two(n: int) -> int:
        p = 1
        while p < n:
            p *= 2
        return p

    @staticmethod
    def _single_elim_slots(capacity: int) -> List[tuple]:
        """Return [(round_number, match_count)] for a single elimination bracket.
        Always uses a power-of-2 bracket size so every round pairs up evenly.
        """
        n = MatchService._next_power_of_two(max(capacity, 2))
        slots = []
        remaining = n
        round_num = 1
        while remaining > 1:
            slots.append((round_num, remaining // 2))
            remaining //= 2
            round_num += 1
        return slots

    @staticmethod
    def _double_elim_slots(capacity: int) -> List[tuple]:
        """Return [(round_number, match_count)] for a double elimination bracket.

        WB rounds: 1..k
        LB rounds: 101..100+2*(k-1)  (pairs: drop-in + pure, alternating)
        Grand Final: 200
        """
        n = MatchService._next_power_of_two(max(capacity, 2))
        k = int(math.log2(n))
        slots = []

        # Winners bracket
        remaining = n
        for r in range(1, k + 1):
            slots.append((r, remaining // 2))
            remaining //= 2

        # Losers bracket: 2*(k-1) rounds in pairs
        lb_count = max(n // 4, 1)
        for j in range(1, 2 * (k - 1) + 1):
            slots.append((100 + j, lb_count))
            if j % 2 == 0:
                lb_count = max(lb_count // 2, 1)

        # Grand Final
        slots.append((200, 1))

        return slots
