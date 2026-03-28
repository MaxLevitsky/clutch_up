# Feature: F001, F002, F003
# Scenario: All Scenarios
# Player Repository

from sqlalchemy.orm import Session
from app.models.player import Player
from typing import Optional


class PlayerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, player_id: int) -> Optional[Player]:
        return self.db.query(Player).filter(Player.id == player_id).first()

    def get_by_username(self, username: str) -> Optional[Player]:
        return self.db.query(Player).filter(Player.username == username).first()

    def get_by_email(self, email: str) -> Optional[Player]:
        return self.db.query(Player).filter(Player.email == email).first()

    def create(self, username: str, email: str, region: str) -> Player:
        player = Player(username=username, email=email, region=region)
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player

    def update_progression_level(self, player_id: int, level: int) -> Optional[Player]:
        player = self.get_by_id(player_id)
        if player:
            player.progression_level = level
            self.db.commit()
            self.db.refresh(player)
        return player
