# Feature: ClutchUp Main Application
# Traceability: All Features

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.api import tournaments, teams, players
from app.models.player import Player, RankTier
import logging

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)


def seed_default_player():
    """
    Seed default player (id=1) for team creation.
    Feature: FR-006a - Allow team creation through website
    Traceability: TC-FR-006a-01
    """
    db = SessionLocal()
    try:
        # Check if default player already exists
        existing_player = db.query(Player).filter(Player.id == 1).first()
        if existing_player:
            logger.info("Default player (id=1) already exists. Skipping seeding.")
            return

        # Create default player
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
        db.commit()
        logger.info("Successfully created default player (id=1)")
    except Exception as e:
        logger.error(f"Failed to seed default player: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# Seed default player on startup
seed_default_player()

app = FastAPI(
    title="ClutchUp API",
    description="Beginner-Friendly Competitive Gaming Platform API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tournaments.router)
app.include_router(teams.router)
app.include_router(players.router)


@app.get("/")
def root():
    return {
        "message": "ClutchUp API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
