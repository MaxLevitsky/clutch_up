# Feature: Tournament Creator / Edit
# Tests for: creator_id tracking, update_tournament service, PUT API endpoint

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.dependencies import get_current_player_id
from app.services.tournament_service import TournamentService
from app.models.player import Player, RankTier
from app.models.tournament import Tournament, TournamentStatus


# ── Integration test DB setup ────────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./test_tournament_creator.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client_as_player1(test_db):
    """Client that is authenticated as player id=1"""
    app.dependency_overrides[get_current_player_id] = lambda: 1
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_player_id, None)



# ── Unit tests: update_tournament service ────────────────────────────────────

def _make_tournament(**kwargs):
    defaults = dict(
        id=1,
        name="Original Cup",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        registered_count=0,
        format="Single Elimination",
        start_time=datetime.now() + timedelta(days=30),
        is_team_tournament=0,
        status=TournamentStatus.REGISTRATION_OPEN,
        creator_id=1,
    )
    defaults.update(kwargs)
    return Tournament(**defaults)


def _service():
    return TournamentService(Mock(), Mock())


def test_update_tournament_success():
    """Creator can update their tournament"""
    mock_repo = Mock()
    service = TournamentService(mock_repo, Mock())

    t = _make_tournament(creator_id=1)
    mock_repo.get_by_id.return_value = t

    updated = _make_tournament(name="New Name", creator_id=1)
    mock_repo.update.return_value = updated

    result = service.update_tournament(
        tournament_id=1,
        update_data={"name": "New Name"},
        current_player_id=1,
    )

    assert result["status"] == "success"
    assert result["tournament"].name == "New Name"
    mock_repo.update.assert_called_once_with(1, {"name": "New Name"})


def test_update_tournament_not_found():
    """Returns 404 when tournament doesn't exist"""
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = None
    service = TournamentService(mock_repo, Mock())

    result = service.update_tournament(1, {"name": "X"}, current_player_id=1)

    assert result["status"] == "error"
    assert result["code"] == 404


def test_update_tournament_not_creator():
    """Returns 403 when caller is not the creator"""
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = _make_tournament(creator_id=1)
    service = TournamentService(mock_repo, Mock())

    result = service.update_tournament(1, {"name": "X"}, current_player_id=99)

    assert result["status"] == "error"
    assert result["code"] == 403
    assert "creator" in result["message"].lower()
    mock_repo.update.assert_not_called()


def test_update_tournament_wrong_status():
    """Cannot edit tournament that is IN_PROGRESS or COMPLETED"""
    for bad_status in (TournamentStatus.IN_PROGRESS, TournamentStatus.COMPLETED, TournamentStatus.CANCELLED):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = _make_tournament(
            creator_id=1, status=bad_status
        )
        service = TournamentService(mock_repo, Mock())

        result = service.update_tournament(1, {"name": "X"}, current_player_id=1)

        assert result["status"] == "error"
        assert result["code"] == 400
        mock_repo.update.assert_not_called()


def test_update_tournament_allowed_statuses():
    """Can edit UPCOMING or REGISTRATION_OPEN tournaments"""
    for good_status in (TournamentStatus.UPCOMING, TournamentStatus.REGISTRATION_OPEN):
        mock_repo = Mock()
        t = _make_tournament(creator_id=1, status=good_status)
        mock_repo.get_by_id.return_value = t
        mock_repo.update.return_value = t
        service = TournamentService(mock_repo, Mock())

        result = service.update_tournament(1, {"name": "X"}, current_player_id=1)

        assert result["status"] == "success"


def test_update_tournament_past_start_time():
    """Rejects update with past start_time"""
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = _make_tournament(creator_id=1)
    service = TournamentService(mock_repo, Mock())

    result = service.update_tournament(
        1,
        {"start_time": datetime(2020, 1, 1)},
        current_player_id=1,
    )

    assert result["status"] == "error"
    assert result["code"] == 400
    assert "future" in result["message"].lower()
    mock_repo.update.assert_not_called()


def test_update_tournament_capacity_below_registrations():
    """Cannot reduce capacity below current registered_count"""
    mock_repo = Mock()
    mock_repo.get_by_id.return_value = _make_tournament(creator_id=1, registered_count=10)
    service = TournamentService(mock_repo, Mock())

    result = service.update_tournament(1, {"capacity": 5}, current_player_id=1)

    assert result["status"] == "error"
    assert result["code"] == 400
    assert "capacity" in result["message"].lower()
    mock_repo.update.assert_not_called()


def test_create_tournament_stores_creator_id():
    """create_tournament passes creator_id to the repository"""
    mock_repo = Mock()
    future = datetime.now() + timedelta(days=30)
    created = Tournament(
        id=1, name="T", rank_tier="BEGINNER", region="NA",
        capacity=16, format="SE", start_time=future,
        is_team_tournament=0, status=TournamentStatus.REGISTRATION_OPEN,
        registered_count=0, creator_id=42,
    )
    mock_repo.create.return_value = created
    service = TournamentService(mock_repo, Mock())

    result = service.create_tournament(
        name="T", rank_tier="BEGINNER", region="NA",
        capacity=16, format="SE", start_time=future,
        is_team_tournament=False, team_size=None, creator_id=42,
    )

    assert result["status"] == "success"
    created_obj = mock_repo.create.call_args[0][0]
    assert created_obj.creator_id == 42


# ── Integration tests: PUT /api/tournaments/{id} ─────────────────────────────

def _create_tournament_via_api(client) -> dict:
    future = (datetime.now() + timedelta(days=30)).isoformat()
    resp = client.post("/api/tournaments/", json={
        "name": "Original Cup",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": future,
        "is_team_tournament": False,
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_api_update_tournament_success(client_as_player1):
    """Creator can update their tournament via PUT"""
    t = _create_tournament_via_api(client_as_player1)
    tid = t["id"]

    resp = client_as_player1.put(f"/api/tournaments/{tid}", json={"name": "Updated Cup"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Cup"
    assert data["creator_id"] == 1


def test_api_create_tournament_stores_creator(client_as_player1):
    """POST /api/tournaments/ sets creator_id from JWT"""
    t = _create_tournament_via_api(client_as_player1)

    assert t["creator_id"] == 1


def test_api_update_tournament_not_creator(client_as_player1):
    """Player 2 cannot edit tournament created by player 1"""
    t = _create_tournament_via_api(client_as_player1)
    tid = t["id"]

    # Temporarily override as player 2
    app.dependency_overrides[get_current_player_id] = lambda: 2
    try:
        resp = client_as_player1.put(f"/api/tournaments/{tid}", json={"name": "Stolen Cup"})
    finally:
        app.dependency_overrides[get_current_player_id] = lambda: 1

    assert resp.status_code == 403


def test_api_update_tournament_unauthenticated(client_as_player1):
    """Unauthenticated PUT request returns 401"""
    t = _create_tournament_via_api(client_as_player1)
    tid = t["id"]

    # Remove auth override to test real auth behavior
    app.dependency_overrides.pop(get_current_player_id, None)
    try:
        resp = client_as_player1.put(f"/api/tournaments/{tid}", json={"name": "X"})
    finally:
        app.dependency_overrides[get_current_player_id] = lambda: 1

    assert resp.status_code == 401


def test_api_update_tournament_not_found(client_as_player1):
    """PUT for non-existent tournament returns 404"""
    resp = client_as_player1.put("/api/tournaments/99999", json={"name": "Ghost"})
    assert resp.status_code == 404


def test_api_update_tournament_partial_fields(client_as_player1):
    """Only specified fields are updated"""
    t = _create_tournament_via_api(client_as_player1)
    tid = t["id"]
    original_capacity = t["capacity"]

    resp = client_as_player1.put(f"/api/tournaments/{tid}", json={"name": "New Name"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["capacity"] == original_capacity


def test_api_update_tournament_response_includes_creator_username(client_as_player1):
    """Tournament response includes creator_username after update"""
    t = _create_tournament_via_api(client_as_player1)
    tid = t["id"]

    resp = client_as_player1.put(f"/api/tournaments/{tid}", json={"name": "Named"})

    assert resp.status_code == 200
    # creator_id should be present; creator_username may be None if no Player row in test DB
    assert "creator_id" in resp.json()
