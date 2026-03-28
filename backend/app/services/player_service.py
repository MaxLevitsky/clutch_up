# Feature: F001, F002, F003
# Scenario: All Scenarios
# Player Service

from app.repositories.player_repository import PlayerRepository
from app.models.player import Player
from typing import Optional


class PlayerService:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    def create_player(self, username: str, email: str, region: str) -> Player:
        # Validate uniqueness
        if self.player_repo.get_by_username(username):
            raise ValueError("Username already exists")
        if self.player_repo.get_by_email(email):
            raise ValueError("Email already exists")

        return self.player_repo.create(username, email, region)

    def get_player(self, player_id: int) -> Optional[Player]:
        return self.player_repo.get_by_id(player_id)

    def update_progression(self, player_id: int, level: int) -> Optional[Player]:
        return self.player_repo.update_progression_level(player_id, level)
