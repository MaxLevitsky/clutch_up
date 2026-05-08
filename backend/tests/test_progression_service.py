# Feature: F003
# Scenario: SC005
# Requirement: FR-11, FR-12
# Test Cases: TC-FR-005-01 through TC-FR-005-09

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.player import Player, RankTier
from app.models.badge import Badge
from app.models.progression import Progression
from app.services.progression_service import (
    ProgressionService,
    BADGE_FIRST_STEPS, BADGE_TEAM_PLAYER, BADGE_MATCH_VICTOR,
    BADGE_CHAMPION, BADGE_VETERAN,
    POINTS_PARTICIPATION, POINTS_MATCH_WIN, POINTS_RUNNER_UP, POINTS_CHAMPION,
)
from app.repositories.progression_repository import ProgressionRepository

TEST_DATABASE_URL = "sqlite:///./test_progression.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_BADGE_SEED = [
    {"id": 1, "name": "First Steps", "description": "First tournament", "criteria": "c1", "icon_url": None},
    {"id": 2, "name": "Team Player", "description": "Join a team", "criteria": "c2", "icon_url": None},
    {"id": 3, "name": "Match Victor", "description": "Win a match", "criteria": "c3", "icon_url": None},
    {"id": 4, "name": "Champion", "description": "Win a tournament", "criteria": "c4", "icon_url": None},
    {"id": 5, "name": "Veteran", "description": "10 tournaments", "criteria": "c5", "icon_url": None},
]


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    for b in _BADGE_SEED:
        if not session.query(Badge).filter(Badge.id == b["id"]).first():
            session.add(Badge(**b))
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _player(db, name: str) -> int:
    p = Player(
        username=name, email=f"{name}@t.com", region="NA",
        rank=RankTier.BEGINNER, account_status="ACTIVE", progression_level=1,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p.id


def _prog(db, player_id: int) -> Progression:
    db.expire_all()
    return db.query(Progression).filter(Progression.player_id == player_id).first()


# ─── Points ───────────────────────────────────────────────────────────────────

def test_tournament_participation_awards_10_points(db):
    """TC-FR-005-01 — Participation in a tournament awards +10 points."""
    pid = _player(db, "p01")
    ProgressionService(db).award_tournament_participation(pid)
    assert _prog(db, pid).points == POINTS_PARTICIPATION


def test_match_win_awards_25_points(db):
    """TC-FR-005-02 — Winning a match awards +25 points."""
    pid = _player(db, "p02")
    ProgressionService(db).award_match_win(pid)
    assert _prog(db, pid).points == POINTS_MATCH_WIN


def test_runner_up_awards_50_points(db):
    """TC-FR-005-03 — Tournament runner-up (2nd place) awards +50 points."""
    pid = _player(db, "p03")
    ProgressionService(db).award_tournament_placement(pid, placement=2)
    assert _prog(db, pid).points == POINTS_RUNNER_UP


def test_champion_awards_100_points(db):
    """TC-FR-005-04 — Tournament winner (1st place) awards +100 points."""
    pid = _player(db, "p04")
    ProgressionService(db).award_tournament_placement(pid, placement=1)
    assert _prog(db, pid).points == POINTS_CHAMPION


def test_points_accumulate_across_awards(db):
    """TC-FR-005-05 — Multiple awards accumulate correctly."""
    pid = _player(db, "p05")
    svc = ProgressionService(db)
    svc.award_tournament_participation(pid)   # +10
    svc.award_match_win(pid)                  # +25
    assert _prog(db, pid).points == POINTS_PARTICIPATION + POINTS_MATCH_WIN


# ─── Levels ───────────────────────────────────────────────────────────────────

def test_level_increases_every_100_points(db):
    """TC-FR-005-06 — Level = 1 + points // 100."""
    pid = _player(db, "p06")
    ProgressionRepository(db).update_points(pid, 250)
    prog = _prog(db, pid)
    assert prog.level == 3   # 1 + 250//100


def test_level_capped_at_50(db):
    """TC-FR-005-07 — Level is capped at 50 regardless of points."""
    pid = _player(db, "p07")
    ProgressionRepository(db).update_points(pid, 10000)
    assert _prog(db, pid).level == 50


# ─── Badges ───────────────────────────────────────────────────────────────────

def test_first_steps_badge_on_first_tournament(db):
    """TC-FR-005-08 — First Steps badge awarded on first tournament registration."""
    pid = _player(db, "p08")
    ProgressionService(db).award_tournament_participation(pid)
    badges = _prog(db, pid).badges.split(",")
    assert str(BADGE_FIRST_STEPS) in badges


def test_team_player_badge_on_team_join(db):
    """TC-FR-005-09 — Team Player badge awarded when joining a team."""
    pid = _player(db, "p09")
    ProgressionService(db).award_team_join(pid)
    badges = _prog(db, pid).badges.split(",")
    assert str(BADGE_TEAM_PLAYER) in badges


def test_champion_badge_on_tournament_win(db):
    """TC-FR-005-10 — Champion badge awarded on tournament victory."""
    pid = _player(db, "p10")
    ProgressionService(db).award_tournament_placement(pid, placement=1)
    badges = _prog(db, pid).badges.split(",")
    assert str(BADGE_CHAMPION) in badges


def test_runner_up_does_not_receive_champion_badge(db):
    """TC-FR-005-11 — Runner-up (2nd place) does NOT receive Champion badge."""
    pid = _player(db, "p11")
    ProgressionService(db).award_tournament_placement(pid, placement=2)
    badges = [b for b in _prog(db, pid).badges.split(",") if b]
    assert str(BADGE_CHAMPION) not in badges


def test_badge_not_awarded_twice(db):
    """TC-FR-005-12 — Same badge is never awarded more than once."""
    pid = _player(db, "p12")
    svc = ProgressionService(db)
    svc.award_team_join(pid)
    svc.award_team_join(pid)
    badges = [b for b in _prog(db, pid).badges.split(",") if b]
    assert badges.count(str(BADGE_TEAM_PLAYER)) == 1


# ─── get_player_progression ───────────────────────────────────────────────────

def test_get_player_progression_returns_complete_data(db):
    """TC-FR-005-13 — get_player_progression returns all required fields."""
    pid = _player(db, "p13")
    svc = ProgressionService(db)
    svc.award_tournament_participation(pid)
    data = svc.get_player_progression(pid)

    assert data["player_id"] == pid
    assert data["points"] == POINTS_PARTICIPATION
    assert data["level"] >= 1
    assert isinstance(data["badges"], list)
    assert data["points_to_next_level"] == 100 - POINTS_PARTICIPATION
    assert data["tournaments_played"] >= 0


def test_get_player_progression_creates_record_if_missing(db):
    """TC-FR-005-14 — Querying progression for new player auto-creates record."""
    pid = _player(db, "p14")
    data = ProgressionService(db).get_player_progression(pid)
    assert data["points"] == 0
    assert data["level"] == 1
