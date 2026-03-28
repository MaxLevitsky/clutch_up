# Feature: F001
# Scenario: SC001, SC002
# Tournament Service - Business Logic for Tournament Registration and Eligibility

from app.repositories.tournament_repository import TournamentRepository
from app.repositories.player_repository import PlayerRepository
from app.models.tournament import Tournament
from typing import List, Dict, Any


class TournamentService:
    def __init__(self, tournament_repo: TournamentRepository, player_repo: PlayerRepository):
        self.tournament_repo = tournament_repo
        self.player_repo = player_repo

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
