# Feature: F002
# Scenario: SC003, SC004
# Team Service - Business Logic for Team Management

from app.repositories.team_repository import TeamRepository
from app.repositories.player_repository import PlayerRepository
from app.repositories.tournament_repository import TournamentRepository
from typing import Dict, Any, Optional


class TeamService:
    def __init__(
        self,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
        tournament_repo: TournamentRepository
    ):
        self.team_repo = team_repo
        self.player_repo = player_repo
        self.tournament_repo = tournament_repo

    def create_team(self, name: str, owner_id: int, badge: Optional[str] = None) -> Dict[str, Any]:
        """
        Feature: F002
        Scenario: SC003
        Requirement: FR-6
        Create a new team with unique name validation
        """
        # Validate player exists
        player = self.player_repo.get_by_id(owner_id)
        if not player:
            return {
                "status": "error",
                "message": "Player not found"
            }

        # Validate unique name (FR-6)
        existing_team = self.team_repo.get_by_name(name)
        if existing_team:
            return {
                "status": "error",
                "message": "Team name already exists. Please choose a different name."
            }

        try:
            team = self.team_repo.create(name, owner_id, badge)
            return {
                "status": "success",
                "message": "Team created successfully",
                "team": team
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to create team",
                "error": str(e)
            }

    def create_invite(self, team_id: int, owner_id: int) -> Dict[str, Any]:
        """
        Feature: F002
        Scenario: SC003
        Requirement: FR-7
        Generate shareable team invite link
        """
        team = self.team_repo.get_by_id(team_id)
        if not team:
            return {
                "status": "error",
                "message": "Team not found"
            }

        # Validate owner
        if team.owner_id != owner_id:
            return {
                "status": "error",
                "message": "Only the team owner can create invites"
            }

        try:
            invite = self.team_repo.create_invite(team_id, owner_id)
            return {
                "status": "success",
                "message": "Invite created successfully",
                "invite": invite
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to create invite",
                "error": str(e)
            }

    def accept_invite(self, token: str, player_id: int) -> Dict[str, Any]:
        """
        Feature: F002
        Scenario: SC003
        Requirement: FR-7
        Accept team invite and join roster
        """
        invite = self.team_repo.get_invite_by_token(token)
        if not invite:
            return {
                "status": "error",
                "message": "Invalid invite link"
            }

        player = self.player_repo.get_by_id(player_id)
        if not player:
            return {
                "status": "error",
                "message": "Player not found"
            }

        success = self.team_repo.accept_invite(token, player_id)
        if success:
            team = self.team_repo.get_by_id(invite.team_id)
            return {
                "status": "success",
                "message": f"Successfully joined {team.name}",
                "team": team
            }
        else:
            return {
                "status": "error",
                "message": "Invite link is invalid, expired, or already used"
            }

    def get_team_roster(self, team_id: int) -> Dict[str, Any]:
        """
        Feature: F002
        Scenario: SC003
        Requirement: FR-8
        Display current roster status
        """
        team = self.team_repo.get_by_id(team_id)
        if not team:
            return {
                "status": "error",
                "message": "Team not found"
            }

        members = self.team_repo.get_team_members(team_id)
        member_count = len(members)

        return {
            "status": "success",
            "team": team,
            "members": members,
            "member_count": member_count
        }

    def validate_team_tournament_eligibility(
        self, team_id: int, tournament_id: int
    ) -> Dict[str, Any]:
        """
        Feature: F002
        Scenario: SC004
        Requirement: FR-9
        Validate team size and eligibility for team tournament
        """
        team = self.team_repo.get_by_id(team_id)
        if not team:
            return {
                "eligible": False,
                "reason": "Team not found",
                "user_message": "Team not found"
            }

        tournament = self.tournament_repo.get_by_id(tournament_id)
        if not tournament:
            return {
                "eligible": False,
                "reason": "Tournament not found",
                "user_message": "Tournament not found"
            }

        # Check if it's a team tournament
        if tournament.is_team_tournament == 0:
            return {
                "eligible": False,
                "reason": "Not a team tournament",
                "user_message": "This is not a team tournament"
            }

        # Check team size (FR-9)
        member_count = self.team_repo.get_team_member_count(team_id)
        required_size = tournament.team_size or 1

        if member_count < required_size:
            return {
                "eligible": False,
                "reason": "Insufficient team size",
                "user_message": f"Your team needs at least {required_size} members. Currently has {member_count}."
            }

        # Check capacity
        if tournament.registered_count >= tournament.capacity:
            return {
                "eligible": False,
                "reason": "Tournament full",
                "user_message": "This tournament is already full"
            }

        return {
            "eligible": True,
            "reason": "All checks passed",
            "user_message": "Your team is eligible for this tournament"
        }

    def register_team_for_tournament(
        self, team_id: int, tournament_id: int, owner_id: int
    ) -> Dict[str, Any]:
        """
        Feature: F002
        Scenario: SC004
        Requirement: FR-9, FR-10
        Register team for tournament and lock roster
        """
        team = self.team_repo.get_by_id(team_id)
        if not team:
            return {
                "status": "error",
                "message": "Team not found"
            }

        # Validate owner
        if team.owner_id != owner_id:
            return {
                "status": "error",
                "message": "Only the team owner can register for tournaments"
            }

        # Validate eligibility
        eligibility = self.validate_team_tournament_eligibility(team_id, tournament_id)
        if not eligibility["eligible"]:
            return {
                "status": "error",
                "message": eligibility["user_message"],
                "eligibility": eligibility
            }

        # Register all team members
        try:
            members = self.team_repo.get_team_members(team_id)
            for member in members:
                self.tournament_repo.register_player(
                    tournament_id, member.player_id, team_id
                )

            tournament = self.tournament_repo.get_by_id(tournament_id)
            return {
                "status": "success",
                "message": f"Team successfully registered for {tournament.name}",
                "tournament_id": tournament_id,
                "team_id": team_id,
                "roster_locked": True,
                "member_count": len(members)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to register team",
                "error": str(e)
            }

    def revoke_invite(self, token: str, owner_id: int) -> Dict[str, Any]:
        """
        Feature: F002
        Requirement: NFR-7
        Revoke team invite link
        """
        invite = self.team_repo.get_invite_by_token(token)
        if not invite:
            return {
                "status": "error",
                "message": "Invite not found"
            }

        team = self.team_repo.get_by_id(invite.team_id)
        if not team or team.owner_id != owner_id:
            return {
                "status": "error",
                "message": "Only the team owner can revoke invites"
            }

        success = self.team_repo.revoke_invite(token)
        if success:
            return {
                "status": "success",
                "message": "Invite revoked successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to revoke invite"
            }
