# Feature: F003
# Scenario: SC005
# Test Cases: Match creation, result recording, progression trigger, tournament finalization

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.player import Player, RankTier
from app.models.tournament import Tournament, TournamentStatus
from app.models.badge import Badge
from app.models.progression import Progression
from app.services.match_service import MatchService

TEST_DATABASE_URL = "sqlite:///./test_match_service.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_BADGE_SEED = [
    {"id": 1, "name": "First Steps", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 2, "name": "Team Player", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 3, "name": "Match Victor", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 4, "name": "Champion", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 5, "name": "Veteran", "description": "d", "criteria": "c", "icon_url": None},
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


def _tournament(db) -> int:
    t = Tournament(
        name="Match Cup", rank_tier="BEGINNER", region="NA",
        capacity=16, registered_count=2,
        status=TournamentStatus.IN_PROGRESS,
        start_time=datetime.utcnow(),
        format="Single Elimination", is_team_tournament=0,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t.id


def _create_match(db, p1, p2, t_id):
    svc = MatchService(db)
    result = svc.create_match(
        tournament_id=t_id, player1_id=p1, player2_id=p2,
        round_number=1, scheduled_time=datetime.utcnow() + timedelta(hours=1),
    )
    return result["match"].id


# ─── Creation ─────────────────────────────────────────────────────────────────

def test_create_match_success(db):
    """Match is created successfully with SCHEDULED status."""
    from app.models.match import MatchStatus
    p1, p2 = _player(db, "cm1"), _player(db, "cm2")
    t_id = _tournament(db)
    result = MatchService(db).create_match(
        tournament_id=t_id, player1_id=p1, player2_id=p2,
        round_number=1, scheduled_time=datetime.utcnow() + timedelta(hours=1),
    )
    assert result["status"] == "success"
    assert result["match"].player1_id == p1
    assert result["match"].player2_id == p2
    assert result["match"].status == MatchStatus.SCHEDULED


def test_create_match_nonexistent_tournament_fails(db):
    """Match creation fails when tournament does not exist."""
    p1, p2 = _player(db, "cn1"), _player(db, "cn2")
    result = MatchService(db).create_match(
        tournament_id=99999, player1_id=p1, player2_id=p2,
        round_number=1, scheduled_time=datetime.utcnow() + timedelta(hours=1),
    )
    assert result["status"] == "error"


def test_create_match_same_player_rejected(db):
    """A player cannot be matched against themselves."""
    p1 = _player(db, "sp1")
    t_id = _tournament(db)
    result = MatchService(db).create_match(
        tournament_id=t_id, player1_id=p1, player2_id=p1,
        round_number=1, scheduled_time=datetime.utcnow() + timedelta(hours=1),
    )
    assert result["status"] == "error"


# ─── Result recording ─────────────────────────────────────────────────────────

def test_record_result_marks_match_completed(db):
    """TC-FR-005: Recording result transitions match to COMPLETED."""
    from app.models.match import MatchStatus
    p1, p2 = _player(db, "rr1"), _player(db, "rr2")
    t_id = _tournament(db)
    m_id = _create_match(db, p1, p2, t_id)

    result = MatchService(db).record_result(match_id=m_id, winner_id=p1, loser_id=p2)
    assert result["status"] == "success"
    assert result["match"].status == MatchStatus.COMPLETED
    assert result["match"].winner_id == p1
    assert result["match"].loser_id == p2


def test_record_result_awards_25_points_to_winner(db):
    """TC-FR-005: Match winner receives +25 progression points."""
    p1, p2 = _player(db, "rp1"), _player(db, "rp2")
    t_id = _tournament(db)
    m_id = _create_match(db, p1, p2, t_id)

    MatchService(db).record_result(match_id=m_id, winner_id=p1, loser_id=p2)

    db.expire_all()
    prog = db.query(Progression).filter(Progression.player_id == p1).first()
    assert prog is not None
    assert prog.points >= 25


def test_record_result_awards_match_victor_badge(db):
    """TC-FR-005: Match winner receives Match Victor badge after first win."""
    from app.services.progression_service import BADGE_MATCH_VICTOR
    p1, p2 = _player(db, "rv1"), _player(db, "rv2")
    t_id = _tournament(db)
    m_id = _create_match(db, p1, p2, t_id)

    MatchService(db).record_result(match_id=m_id, winner_id=p1, loser_id=p2)

    db.expire_all()
    prog = db.query(Progression).filter(Progression.player_id == p1).first()
    assert prog is not None
    badges = [b for b in (prog.badges or "").split(",") if b]
    assert str(BADGE_MATCH_VICTOR) in badges


def test_record_result_on_completed_match_fails(db):
    """Cannot record a result on a match that is already COMPLETED."""
    p1, p2 = _player(db, "rc1"), _player(db, "rc2")
    t_id = _tournament(db)
    m_id = _create_match(db, p1, p2, t_id)

    svc = MatchService(db)
    svc.record_result(match_id=m_id, winner_id=p1, loser_id=p2)

    second = svc.record_result(match_id=m_id, winner_id=p2, loser_id=p1)
    assert second["status"] == "error"
    assert "already completed" in second["message"]


def test_record_result_nonexistent_match_fails(db):
    """Recording a result for a non-existent match returns error."""
    p1, p2 = _player(db, "rn1"), _player(db, "rn2")
    result = MatchService(db).record_result(match_id=99999, winner_id=p1, loser_id=p2)
    assert result["status"] == "error"


# ─── Tournament finalization ───────────────────────────────────────────────────

def test_tournament_finalizes_when_last_match_completes(db):
    """TC-FR-005: Tournament transitions to COMPLETED when all matches finish."""
    p1, p2 = _player(db, "tf1"), _player(db, "tf2")
    t_id = _tournament(db)
    m_id = _create_match(db, p1, p2, t_id)

    MatchService(db).record_result(match_id=m_id, winner_id=p1, loser_id=p2)

    db.expire_all()
    tournament = db.query(Tournament).filter(Tournament.id == t_id).first()
    assert tournament.status == TournamentStatus.COMPLETED


def test_tournament_winner_receives_champion_points_and_badge(db):
    """TC-FR-005: Tournament winner receives +100 pts and Champion badge."""
    from app.services.progression_service import POINTS_CHAMPION, BADGE_CHAMPION
    p1, p2 = _player(db, "tc1"), _player(db, "tc2")
    t_id = _tournament(db)
    m_id = _create_match(db, p1, p2, t_id)

    MatchService(db).record_result(match_id=m_id, winner_id=p1, loser_id=p2)

    db.expire_all()
    prog = db.query(Progression).filter(Progression.player_id == p1).first()
    # Winner gets match win points + champion points
    assert prog.points >= POINTS_CHAMPION
    badges = [b for b in (prog.badges or "").split(",") if b]
    assert str(BADGE_CHAMPION) in badges
