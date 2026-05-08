# Feature: Full Tournament Flow
# Tests for: bracket generation with player assignment, winner advancement, round progression,
#            bye handling, result recording auth (API)

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.dependencies import get_current_player_id
from app.models.player import Player, RankTier
from app.models.tournament import Tournament, TournamentStatus
from app.models.tournament_registration import TournamentRegistration
from app.models.match import Match, MatchStatus
from app.models.badge import Badge
from app.services.match_service import MatchService

# ── DB setup ────────────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./test_tournament_flow.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_BADGE_SEED = [
    {"id": 1, "name": "First Steps", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 2, "name": "Team Player", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 3, "name": "Match Victor", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 4, "name": "Champion", "description": "d", "criteria": "c", "icon_url": None},
    {"id": 5, "name": "Veteran", "description": "d", "criteria": "c", "icon_url": None},
]


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _ensure_db_override():
    """Re-assert this module's DB override before each test to prevent cross-module contamination."""
    app.dependency_overrides[get_db] = override_get_db
    yield


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


@pytest.fixture
def client_as_creator(db):
    app.dependency_overrides[get_current_player_id] = lambda: 1
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_player_id, None)


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _add_player(db, name: str) -> int:
    p = Player(
        username=name, email=f"{name}@t.com", region="NA",
        rank=RankTier.BEGINNER, account_status="ACTIVE", progression_level=1,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p.id


def _make_tournament(db, capacity=4, creator_id=1) -> Tournament:
    future = datetime.now() + timedelta(days=30)
    t = Tournament(
        name="Flow Cup", rank_tier="BEGINNER", region="NA",
        capacity=capacity, registered_count=0,
        status=TournamentStatus.REGISTRATION_OPEN,
        start_time=future, format="Single Elimination",
        is_team_tournament=0, creator_id=creator_id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _register(db, tournament_id: int, player_id: int):
    reg = TournamentRegistration(tournament_id=tournament_id, player_id=player_id)
    db.add(reg)
    db.commit()


def _create_via_api(client) -> dict:
    future = (datetime.now() + timedelta(days=30)).isoformat()
    resp = client.post("/api/tournaments/", json={
        "name": "Flow Cup", "rank_tier": "BEGINNER", "region": "NA",
        "capacity": 4, "format": "Single Elimination",
        "start_time": future, "is_team_tournament": False,
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Unit tests: generate_bracket ────────────────────────────────────────────────

def test_generate_bracket_assigns_players_to_first_round(db):
    """Players are paired into first-round match slots after generate_bracket."""
    t = _make_tournament(db, capacity=4)
    p1 = _add_player(db, "gb1")
    p2 = _add_player(db, "gb2")
    p3 = _add_player(db, "gb3")
    p4 = _add_player(db, "gb4")
    for pid in (p1, p2, p3, p4):
        _register(db, t.id, pid)

    svc = MatchService(db)
    svc.generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    first_round = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 1
    ).order_by(Match.id).all()

    assert len(first_round) == 2
    all_assigned = {first_round[0].player1_id, first_round[0].player2_id,
                    first_round[1].player1_id, first_round[1].player2_id}
    assert all_assigned == {p1, p2, p3, p4}


def test_generate_bracket_sets_tournament_in_progress(db):
    """Tournament status becomes IN_PROGRESS when players are assigned."""
    t = _make_tournament(db, capacity=2)
    p1 = _add_player(db, "ip1")
    p2 = _add_player(db, "ip2")
    _register(db, t.id, p1)
    _register(db, t.id, p2)

    MatchService(db).generate_bracket(t.id, capacity=2, format="Single Elimination", start_time=t.start_time)

    db.expire_all()
    assert db.query(Tournament).filter(Tournament.id == t.id).first().status == TournamentStatus.IN_PROGRESS


def test_generate_bracket_no_players_keeps_registration_open(db):
    """Without registered players, status stays REGISTRATION_OPEN (auto-called at creation)."""
    t = _make_tournament(db, capacity=4)

    MatchService(db).generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    db.expire_all()
    assert db.query(Tournament).filter(Tournament.id == t.id).first().status == TournamentStatus.REGISTRATION_OPEN


def test_generate_bracket_creates_correct_round_structure(db):
    """4-player SE bracket: 2 first-round matches + 1 final slot."""
    t = _make_tournament(db, capacity=4)
    for i in range(4):
        _register(db, t.id, _add_player(db, f"rs{i}"))

    MatchService(db).generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    r1 = db.query(Match).filter(Match.tournament_id == t.id, Match.round_number == 1).count()
    r2 = db.query(Match).filter(Match.tournament_id == t.id, Match.round_number == 2).count()
    assert r1 == 2
    assert r2 == 1


def test_generate_bracket_bye_handling_odd_players(db):
    """Odd player count: last player gets an automatic bye (match auto-completed)."""
    t = _make_tournament(db, capacity=4)
    p1 = _add_player(db, "bye1")
    p2 = _add_player(db, "bye2")
    p3 = _add_player(db, "bye3")
    for pid in (p1, p2, p3):
        _register(db, t.id, pid)

    MatchService(db).generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    completed = db.query(Match).filter(
        Match.tournament_id == t.id,
        Match.status == MatchStatus.COMPLETED,
    ).all()
    assert len(completed) == 1
    # The bye match should have a winner set
    assert completed[0].winner_id is not None


def test_generate_bracket_bye_winner_advances_to_next_round(db):
    """Bye winner is automatically placed in the next-round slot."""
    t = _make_tournament(db, capacity=4)
    p1 = _add_player(db, "byadv1")
    p2 = _add_player(db, "byadv2")
    p3 = _add_player(db, "byadv3")
    for pid in (p1, p2, p3):
        _register(db, t.id, pid)

    MatchService(db).generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    final = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 2
    ).order_by(Match.id).first()
    assert final is not None
    # One slot in the final should already be filled by the bye winner
    assert final.player1_id is not None or final.player2_id is not None


# ── Unit tests: _advance_winner ──────────────────────────────────────────────────

def test_advance_winner_fills_next_round_slot(db):
    """Winner of first match advances to player1_id of the final."""
    t = _make_tournament(db, capacity=4)
    p1 = _add_player(db, "aw1")
    p2 = _add_player(db, "aw2")
    p3 = _add_player(db, "aw3")
    p4 = _add_player(db, "aw4")
    for pid in (p1, p2, p3, p4):
        _register(db, t.id, pid)

    svc = MatchService(db)
    svc.generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    first_round = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 1
    ).order_by(Match.id).all()
    m1 = first_round[0]
    winner = m1.player1_id

    svc.record_result(m1.id, winner_id=winner, loser_id=m1.player2_id)

    db.expire_all()
    final = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 2
    ).first()
    assert final.player1_id == winner


def test_advance_winner_second_match_fills_player2_slot(db):
    """Winner of the second match in a round advances to player2_id of the final."""
    t = _make_tournament(db, capacity=4)
    p1 = _add_player(db, "sw1")
    p2 = _add_player(db, "sw2")
    p3 = _add_player(db, "sw3")
    p4 = _add_player(db, "sw4")
    for pid in (p1, p2, p3, p4):
        _register(db, t.id, pid)

    svc = MatchService(db)
    svc.generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    first_round = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 1
    ).order_by(Match.id).all()
    m2 = first_round[1]
    winner = m2.player1_id

    svc.record_result(m2.id, winner_id=winner, loser_id=m2.player2_id)

    db.expire_all()
    final = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 2
    ).first()
    assert final.player2_id == winner


def test_no_advance_on_final_match(db):
    """Recording the final match result does not crash — no next round exists."""
    t = _make_tournament(db, capacity=2)
    p1 = _add_player(db, "fn1")
    p2 = _add_player(db, "fn2")
    _register(db, t.id, p1)
    _register(db, t.id, p2)

    svc = MatchService(db)
    svc.generate_bracket(t.id, capacity=2, format="Single Elimination", start_time=t.start_time)

    matches = db.query(Match).filter(Match.tournament_id == t.id).order_by(Match.id).all()
    final = matches[0]
    result = svc.record_result(final.id, winner_id=final.player1_id, loser_id=final.player2_id)
    assert result["status"] == "success"

    db.expire_all()
    assert db.query(Tournament).filter(Tournament.id == t.id).first().status == TournamentStatus.COMPLETED


# ── Full 4-player flow: unit ─────────────────────────────────────────────────────

def test_full_4_player_single_elim_flow(db):
    """
    Full end-to-end unit flow:
    4 players → generate bracket → record R1 results → both advance to final
    → record final → tournament COMPLETED.
    """
    t = _make_tournament(db, capacity=4)
    p1 = _add_player(db, "full1")
    p2 = _add_player(db, "full2")
    p3 = _add_player(db, "full3")
    p4 = _add_player(db, "full4")
    for pid in (p1, p2, p3, p4):
        _register(db, t.id, pid)

    svc = MatchService(db)
    svc.generate_bracket(t.id, capacity=4, format="Single Elimination", start_time=t.start_time)

    r1 = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 1
    ).order_by(Match.id).all()

    # Record round 1 results
    svc.record_result(r1[0].id, winner_id=r1[0].player1_id, loser_id=r1[0].player2_id)
    svc.record_result(r1[1].id, winner_id=r1[1].player1_id, loser_id=r1[1].player2_id)

    db.expire_all()
    final = db.query(Match).filter(
        Match.tournament_id == t.id, Match.round_number == 2
    ).first()
    assert final.player1_id is not None
    assert final.player2_id is not None
    assert final.status == MatchStatus.SCHEDULED

    # Record the final
    svc.record_result(final.id, winner_id=final.player1_id, loser_id=final.player2_id)

    db.expire_all()
    assert db.query(Tournament).filter(Tournament.id == t.id).first().status == TournamentStatus.COMPLETED


# ── API integration tests: result recording auth ─────────────────────────────────

def test_api_record_result_requires_auth(db):
    """POST /matches/{id}/result without auth returns 401."""
    app.dependency_overrides.pop(get_current_player_id, None)
    client = TestClient(app)

    t = _make_tournament(db, capacity=2, creator_id=1)
    p1 = _add_player(db, "auth1")
    p2 = _add_player(db, "auth2")
    _register(db, t.id, p1)
    _register(db, t.id, p2)
    MatchService(db).generate_bracket(t.id, capacity=2, format="Single Elimination", start_time=t.start_time)

    match = db.query(Match).filter(Match.tournament_id == t.id).first()
    resp = client.post(f"/api/matches/{match.id}/result", json={"winner_id": p1, "loser_id": p2})
    assert resp.status_code == 401


def test_api_record_result_non_creator_returns_403(db):
    """Non-creator gets 403 when trying to record a result."""
    t = _make_tournament(db, capacity=2, creator_id=1)
    p1 = _add_player(db, "nc1")
    p2 = _add_player(db, "nc2")
    _register(db, t.id, p1)
    _register(db, t.id, p2)
    MatchService(db).generate_bracket(t.id, capacity=2, format="Single Elimination", start_time=t.start_time)

    match = db.query(Match).filter(Match.tournament_id == t.id).first()

    # Authenticate as player 99 (not the creator)
    app.dependency_overrides[get_current_player_id] = lambda: 99
    try:
        resp = TestClient(app).post(f"/api/matches/{match.id}/result",
                                    json={"winner_id": p1, "loser_id": p2})
    finally:
        app.dependency_overrides.pop(get_current_player_id, None)

    assert resp.status_code == 403


def test_api_record_result_creator_succeeds(db):
    """Creator records a result successfully via API."""
    t = _make_tournament(db, capacity=2, creator_id=1)
    p1 = _add_player(db, "cr1")
    p2 = _add_player(db, "cr2")
    _register(db, t.id, p1)
    _register(db, t.id, p2)
    MatchService(db).generate_bracket(t.id, capacity=2, format="Single Elimination", start_time=t.start_time)

    match = db.query(Match).filter(Match.tournament_id == t.id).first()

    app.dependency_overrides[get_current_player_id] = lambda: 1
    try:
        resp = TestClient(app).post(f"/api/matches/{match.id}/result",
                                    json={"winner_id": match.player1_id, "loser_id": match.player2_id})
    finally:
        app.dependency_overrides.pop(get_current_player_id, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "COMPLETED"
    assert data["winner_id"] == match.player1_id


def test_api_full_flow_bracket_and_results(db):
    """
    Integration: create tournament via API, register players, generate bracket via API,
    record both R1 results, verify final is populated.
    """
    app.dependency_overrides[get_current_player_id] = lambda: 1
    client = TestClient(app)

    t_data = _create_via_api(client)
    tid = t_data["id"]

    p1 = _add_player(db, "api1")
    p2 = _add_player(db, "api2")
    p3 = _add_player(db, "api3")
    p4 = _add_player(db, "api4")
    for pid in (p1, p2, p3, p4):
        _register(db, tid, pid)

    # Generate bracket
    resp = client.post(f"/api/tournaments/{tid}/generate-bracket")
    assert resp.status_code == 200

    # Fetch matches
    resp = client.get(f"/api/matches/tournament/{tid}")
    assert resp.status_code == 200
    matches = resp.json()
    r1 = [m for m in matches if m["round_number"] == 1]
    assert len(r1) == 2
    # All first-round players should be assigned
    for m in r1:
        assert m["player1_id"] is not None
        assert m["player2_id"] is not None

    # Record round 1
    for m in r1:
        resp = client.post(f"/api/matches/{m['id']}/result",
                           json={"winner_id": m["player1_id"], "loser_id": m["player2_id"]})
        assert resp.status_code == 200

    # Final should now have both players assigned
    resp = client.get(f"/api/matches/tournament/{tid}")
    final = [m for m in resp.json() if m["round_number"] == 2]
    assert len(final) == 1
    assert final[0]["player1_id"] is not None
    assert final[0]["player2_id"] is not None

    app.dependency_overrides.pop(get_current_player_id, None)
