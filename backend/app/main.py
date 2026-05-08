# Feature: ClutchUp Main Application
# Traceability: All Features

import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.api import tournaments, teams, players
from app.api import auth, progression, matches
from app.models.player import Player, RankTier
from app.models.badge import Badge
from app.models.progression import Progression
from app.models.system_log import SystemLog  # noqa: F401 — ensures table is created
from app.models.product_event import ProductEvent  # noqa: F401 — ensures table is created
from app.models.match import Match  # noqa: F401
from app.models.team import Team  # noqa: F401
from app.models.team_membership import TeamMembership  # noqa: F401
from app.models.team_invite import TeamInvite  # noqa: F401
from app.models.tournament import Tournament  # noqa: F401
from app.models.tournament_registration import TournamentRegistration  # noqa: F401

logger = logging.getLogger(__name__)

# Create all database tables (including new ones)
Base.metadata.create_all(bind=engine)


BADGE_DEFINITIONS = [
    {"id": 1, "name": "First Steps", "description": "Registered for your first tournament", "criteria": "tournaments_played >= 1", "icon_url": None},
    {"id": 2, "name": "Team Player", "description": "Joined a team", "criteria": "team_joined == True", "icon_url": None},
    {"id": 3, "name": "Match Victor", "description": "Won your first match", "criteria": "match_wins >= 1", "icon_url": None},
    {"id": 4, "name": "Champion", "description": "Won a tournament", "criteria": "tournament_wins >= 1", "icon_url": None},
    {"id": 5, "name": "Veteran", "description": "Completed 10 tournaments", "criteria": "tournaments_played >= 10", "icon_url": None},
]


def seed_badges():
    db = SessionLocal()
    try:
        for b in BADGE_DEFINITIONS:
            if not db.query(Badge).filter(Badge.id == b["id"]).first():
                db.add(Badge(**b))
        db.commit()
    except Exception as e:
        logger.error(f"Failed to seed badges: {e}")
        db.rollback()
    finally:
        db.close()


def seed_default_player():
    """
    Seed default player (id=1) for backward compat in dev.
    Feature: FR-006a - Allow team creation through website
    Traceability: TC-FR-006a-01
    """
    db = SessionLocal()
    try:
        existing_player = db.query(Player).filter(Player.id == 1).first()
        if existing_player:
            logger.info("Default player (id=1) already exists. Skipping seeding.")
            return

        default_player = Player(
            id=1,
            username='demo_player',
            email='demo@clutchup.local',
            region='NA',
            rank=RankTier.BEGINNER,
            account_status='ACTIVE',
            progression_level=1
        )
        db.add(default_player)
        db.flush()
        db.add(Progression(player_id=1))
        db.commit()
        logger.info("Successfully created default player (id=1)")
    except Exception as e:
        logger.error(f"Failed to seed default player: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def run_migrations():
    """Apply lightweight schema migrations for columns added after initial release."""
    with engine.connect() as conn:
        # Add password_hash to players if missing
        try:
            conn.execute(text("ALTER TABLE players ADD COLUMN password_hash VARCHAR"))
            conn.commit()
            logger.info("Migration: added password_hash to players")
        except Exception:
            pass  # Column already exists

        # Add match participant columns if missing
        for col, definition in [
            ("round_number", "INTEGER DEFAULT 1"),
            ("player1_id", "INTEGER REFERENCES players(id)"),
            ("player2_id", "INTEGER REFERENCES players(id)"),
            ("winner_id", "INTEGER REFERENCES players(id)"),
            ("loser_id", "INTEGER REFERENCES players(id)"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE matches ADD COLUMN {col} {definition}"))
                conn.commit()
                logger.info(f"Migration: added matches.{col}")
            except Exception:
                pass


from sqlalchemy import text
run_migrations()
seed_badges()
seed_default_player()

app = FastAPI(
    title="ClutchUp API",
    description="Beginner-Friendly Competitive Gaming Platform API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)

    db: Session = SessionLocal()
    try:
        from app.models.system_log import SystemLog
        db.add(SystemLog(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    return response


# Include routers
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(progression.router)
app.include_router(matches.router)


@app.get("/")
def root():
    return {"message": "ClutchUp API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
