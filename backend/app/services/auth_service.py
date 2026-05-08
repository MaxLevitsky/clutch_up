# Feature: Authentication
# Traceability: Infrastructure

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models.player import Player, RankTier
from app.models.progression import Progression

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, email: str, password: str, region: str) -> dict:
        if self.db.query(Player).filter(Player.username == username).first():
            return {"status": "error", "message": "Username already taken"}
        if self.db.query(Player).filter(Player.email == email).first():
            return {"status": "error", "message": "Email already registered"}

        player = Player(
            username=username,
            email=email,
            password_hash=hash_password(password),
            region=region,
            rank=RankTier.BEGINNER,
            account_status="ACTIVE",
        )
        self.db.add(player)
        self.db.flush()

        progression = Progression(player_id=player.id)
        self.db.add(progression)
        self.db.commit()
        self.db.refresh(player)

        token = create_access_token({"sub": str(player.id), "username": player.username})
        return {
            "status": "success",
            "access_token": token,
            "player_id": player.id,
            "username": player.username,
            "rank": player.rank,
        }

    def login(self, username: str, password: str) -> dict:
        player = self.db.query(Player).filter(Player.username == username).first()
        if not player or not player.password_hash or not verify_password(password, player.password_hash):
            return {"status": "error", "message": "Invalid username or password"}

        token = create_access_token({"sub": str(player.id), "username": player.username})
        return {
            "status": "success",
            "access_token": token,
            "player_id": player.id,
            "username": player.username,
            "rank": player.rank,
        }
