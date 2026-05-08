# Feature: F001, F004
# Scenario: SC001, SC002, SC007
# Tournament Service - Business Logic for Tournament Registration, Eligibility, and Creation

from app.repositories.tournament_repository import TournamentRepository
from app.repositories.player_repository import PlayerRepository
from app.models.tournament import Tournament, TournamentStatus
from typing import List, Dict, Any, Optional
from datetime import datetime


class TournamentService:
    def __init__(
        self,
        tournament_repo: TournamentRepository,
        player_repo: PlayerRepository,
        progression_service=None,
    ):
        self.tournament_repo = tournament_repo
        self.player_repo = player_repo
        self.progression_service = progression_service

    def get_eligible_tournaments(self, player_id: int) -> List[Tournament]:
        """
        Feature: F001
        Scenario: SC001
        Requirement: FR-1
        Get tournaments that match player's rank and region
        """
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise ValueError("Player not found")

        return self.tournament_repo.get_eligible_tournaments(player.rank, player.region)

    def validate_eligibility(self, player_id: int, tournament_id: int) -> Dict[str, Any]:
        """
        Feature: F001
        Scenario: SC002
        Requirement: FR-4
        Validate player eligibility for tournament registration
        """
        player = self.player_repo.get_by_id(player_id)
        if not player:
            return {
                "eligible": False,
                "reason": "Player not found",
                "user_message": "Your account could not be found. Please contact support."
            }

        tournament = self.tournament_repo.get_by_id(tournament_id)
        if not tournament:
            return {
                "eligible": False,
                "reason": "Tournament not found",
                "user_message": "This tournament is no longer available."
            }

        # Check account status (FR-4)
        if player.account_status != "ACTIVE":
            return {
                "eligible": False,
                "reason": "Account not active",
                "user_message": "Your account must be active to join tournaments."
            }

        # Check rank (FR-4, FR-5)
        if player.rank != tournament.rank_tier:
            return {
                "eligible": False,
                "reason": "Rank mismatch",
                "user_message": f"This tournament is for {tournament.rank_tier} players. You are currently {player.rank}."
            }

        # Check region (FR-4, FR-5)
        if player.region != tournament.region:
            return {
                "eligible": False,
                "reason": "Region mismatch",
                "user_message": f"This tournament is for {tournament.region} region. You are in {player.region}."
            }

        # Check capacity
        if tournament.registered_count >= tournament.capacity:
            return {
                "eligible": False,
                "reason": "Tournament full",
                "user_message": "This tournament is already full. Please try another tournament."
            }

        # Check duplicate registration (NFR-3)
        if self.tournament_repo.is_player_registered(tournament_id, player_id):
            return {
                "eligible": False,
                "reason": "Already registered",
                "user_message": "You are already registered for this tournament."
            }

        # Check tournament status
        if tournament.status != "REGISTRATION_OPEN":
            return {
                "eligible": False,
                "reason": "Registration not open",
                "user_message": "Registration for this tournament is not currently open."
            }

        return {
            "eligible": True,
            "reason": "All checks passed",
            "user_message": "You are eligible to join this tournament."
        }

    def register_player(self, player_id: int, tournament_id: int) -> Dict[str, Any]:
        """
        Feature: F001
        Scenario: SC001
        Requirement: FR-2, FR-3
        Register player for tournament with validation
        """
        # Validate eligibility first
        eligibility = self.validate_eligibility(player_id, tournament_id)

        if not eligibility["eligible"]:
            return {
                "status": "error",
                "message": eligibility["user_message"],
                "tournament_id": tournament_id,
                "player_id": player_id,
                "eligibility": eligibility
            }

        # Perform registration
        try:
            registration = self.tournament_repo.register_player(tournament_id, player_id)
            tournament = self.tournament_repo.get_by_id(tournament_id)

            # Feature: F003 — award participation points and check badges
            if self.progression_service:
                self.progression_service.award_tournament_participation(player_id)

            return {
                "status": "success",
                "message": f"Successfully registered for {tournament.name}",
                "tournament_id": tournament_id,
                "player_id": player_id,
                "registered_at": registration.registered_at,
                "tournament_details": {
                    "name": tournament.name,
                    "start_time": tournament.start_time,
                    "format": tournament.format
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Registration failed. Please try again.",
                "tournament_id": tournament_id,
                "player_id": player_id,
                "error": str(e)
            }

    def get_all_tournaments(self) -> List[Tournament]:
        """Get all tournaments for admin/display purposes"""
        return self.tournament_repo.get_all_tournaments()

    def create_tournament(
        self,
        name: str,
        rank_tier: str,
        region: str,
        capacity: int,
        format: str,
        start_time: datetime,
        is_team_tournament: bool,
        team_size: int | None,
        creator_id: int | None = None,
    ) -> Dict[str, Any]:
        """
        Feature: F004
        Scenario: SC007
        Requirements: FR-13, FR-14, FR-15, FR-16
        Create a new tournament with validation
        """
        # FR-14: Validate capacity (1-64)
        if capacity < 1 or capacity > 64:
            return {
                "status": "error",
                "message": "Capacity must be between 1 and 64"
            }

        # FR-14: Validate start time (must be in future)
        if start_time <= datetime.now():
            return {
                "status": "error",
                "message": "Start time must be in the future"
            }

        # FR-16: Validate team_size consistency
        if is_team_tournament and team_size is None:
            return {
                "status": "error",
                "message": "Team tournaments must specify team_size"
            }

        if not is_team_tournament and team_size is not None:
            return {
                "status": "error",
                "message": "Solo tournaments must not specify team_size"
            }

        # FR-16: Validate team_size range (2-5)
        if team_size is not None and (team_size < 2 or team_size > 5):
            return {
                "status": "error",
                "message": "Team size must be between 2 and 5"
            }

        # FR-13, FR-15: Create tournament with UPCOMING status and registered_count 0
        try:
            tournament = Tournament(
                name=name,
                rank_tier=rank_tier,
                region=region,
                capacity=capacity,
                format=format,
                start_time=start_time,
                is_team_tournament=1 if is_team_tournament else 0,
                team_size=team_size,
                status=TournamentStatus.REGISTRATION_OPEN,
                registered_count=0,  # FR-15
                creator_id=creator_id,
            )

            created_tournament = self.tournament_repo.create(tournament)

            return {
                "status": "success",
                "message": f"Tournament '{name}' created successfully",
                "tournament": created_tournament
            }

        except Exception as e:
            return {
                "status": "error",
                "message": "Tournament creation failed. Please try again.",
                "error": str(e)
            }

    def update_tournament(
        self,
        tournament_id: int,
        update_data: dict,
        current_player_id: int,
    ) -> Dict[str, Any]:
        tournament = self.tournament_repo.get_by_id(tournament_id)
        if not tournament:
            return {"status": "error", "code": 404, "message": "Tournament not found"}

        if tournament.creator_id != current_player_id:
            return {"status": "error", "code": 403, "message": "Only the creator can edit this tournament"}

        if tournament.status not in (TournamentStatus.UPCOMING, TournamentStatus.REGISTRATION_OPEN):
            return {"status": "error", "code": 400, "message": "Tournament cannot be edited in its current status"}

        if "start_time" in update_data and update_data["start_time"] <= datetime.now():
            return {"status": "error", "code": 400, "message": "Start time must be in the future"}

        if "capacity" in update_data and update_data["capacity"] < tournament.registered_count:
            return {"status": "error", "code": 400, "message": "Capacity cannot be less than current registrations"}

        updated = self.tournament_repo.update(tournament_id, update_data)
        return {"status": "success", "tournament": updated}
