# Feature: F004
# Scenario: SC007
# Test Cases: TC-FR-013-02, TC-NFR-014-01
# Integration tests for tournament creation API endpoint

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.tournament import TournamentStatus
from app.dependencies import get_current_player_id


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_tournament_api.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_player_id] = lambda: 1


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client"""
    return TestClient(app)


def test_api_create_tournament_success(client):
    """
    Test Case: TC-FR-013-02
    Requirement: FR-13
    Feature: F004
    Scenario: SC007
    Create tournament via API endpoint - success case
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "API Test Tournament",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": False
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "API Test Tournament"
    assert data["rank_tier"] == "BEGINNER"
    assert data["region"] == "NA"
    assert data["capacity"] == 16
    assert data["registered_count"] == 0
    assert data["status"] == "REGISTRATION_OPEN"
    assert data["format"] == "Single Elimination"
    assert data["is_team_tournament"] == 0


def test_api_create_tournament_invalid_capacity(client):
    """
    Test Case: TC-FR-014-01 (API level)
    Requirement: FR-14
    Feature: F004
    API endpoint rejects invalid capacity
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "Invalid Tournament",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 0,  # Invalid
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": False
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    # Pydantic validates capacity >= 8, returns 422 for schema validation errors
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_api_create_tournament_past_start_time(client):
    """
    Test Case: TC-FR-014-02 (API level)
    Requirement: FR-14
    Feature: F004
    API endpoint rejects past start time
    """
    # Arrange
    past_time = datetime(2020, 1, 1, 10, 0, 0)
    request_payload = {
        "name": "Past Tournament",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": past_time.isoformat(),
        "is_team_tournament": False
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "future" in data["detail"].lower() or "past" in data["detail"].lower()


def test_api_create_team_tournament_without_team_size(client):
    """
    Test Case: TC-FR-016-01 (API level)
    Requirement: FR-16
    Feature: F004
    API endpoint rejects team tournament without team size
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "Team Tournament",
        "rank_tier": "INTERMEDIATE",
        "region": "EU",
        "capacity": 8,
        "format": "Double Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": True
        # team_size missing
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "team size" in data["detail"].lower() or "team_size" in data["detail"].lower()


def test_api_create_tournament_missing_required_fields(client):
    """
    Integration test: API validation rejects missing required fields
    """
    # Arrange
    incomplete_payload = {
        "name": "Incomplete Tournament",
        "rank_tier": "BEGINNER"
        # Missing: region, capacity, format, start_time
    }

    # Act
    response = client.post("/api/tournaments/", json=incomplete_payload)

    # Assert
    assert response.status_code == 422  # Pydantic validation error


def test_created_tournament_immediately_visible(client):
    """
    Test Case: TC-NFR-014-01
    Requirement: NFR-14
    Feature: F004
    Verify created tournament immediately visible in tournament list
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "Visibility Test Tournament",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": False
    }

    # Act - Create tournament
    create_response = client.post("/api/tournaments/", json=request_payload)
    assert create_response.status_code == 201
    created_tournament = create_response.json()

    # Act - Immediately fetch all tournaments
    list_response = client.get("/api/tournaments/")

    # Assert
    assert list_response.status_code == 200
    tournaments = list_response.json()["tournaments"]

    # Verify created tournament is in the list
    tournament_ids = [t["id"] for t in tournaments]
    assert created_tournament["id"] in tournament_ids

    # Verify tournament has correct attributes
    found_tournament = next(t for t in tournaments if t["id"] == created_tournament["id"])
    assert found_tournament["name"] == "Visibility Test Tournament"
    assert found_tournament["status"] == "REGISTRATION_OPEN"
    assert found_tournament["registered_count"] == 0


def test_api_create_team_tournament_with_team_size(client):
    """
    Integration test: Successfully create team tournament with team size
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "Valid Team Tournament",
        "rank_tier": "INTERMEDIATE",
        "region": "EU",
        "capacity": 8,
        "format": "Double Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": True,
        "team_size": 5
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["is_team_tournament"] == 1
    assert data["team_size"] == 5
    assert data["status"] == "REGISTRATION_OPEN"


def test_api_create_tournament_capacity_exceeds_max(client):
    """
    Test Case: TC-FR-014-03
    Requirement: FR-14
    Feature: F004
    API endpoint rejects capacity > 64
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "Oversized Tournament",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 100,  # Exceeds maximum of 64
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": False
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    assert response.status_code == 422  # Pydantic validation
    data = response.json()
    assert "detail" in data


def test_api_create_tournament_validation_messages(client):
    """
    Test Case: TC-NFR-013-01
    Requirement: NFR-13
    Feature: F004
    Validation errors return clear messages
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)

    # Test 1: Invalid capacity
    invalid_capacity_payload = {
        "name": "Test",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 0,
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": False
    }

    # Act
    response1 = client.post("/api/tournaments/", json=invalid_capacity_payload)

    # Assert
    assert response1.status_code in [400, 422]
    data1 = response1.json()
    assert "detail" in data1

    # Test 2: Past start time
    past_time_payload = {
        "name": "Test",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": datetime(2020, 1, 1).isoformat(),
        "is_team_tournament": False
    }

    # Act
    response2 = client.post("/api/tournaments/", json=past_time_payload)

    # Assert
    assert response2.status_code == 400
    data2 = response2.json()
    assert "detail" in data2
    assert "future" in data2["detail"].lower() or "past" in data2["detail"].lower()

    # Test 3: Team tournament without team_size
    missing_team_size_payload = {
        "name": "Test",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": True
    }

    # Act
    response3 = client.post("/api/tournaments/", json=missing_team_size_payload)

    # Assert
    assert response3.status_code == 400
    data3 = response3.json()
    assert "detail" in data3
    assert "team" in data3["detail"].lower()


def test_api_create_tournament_solo_with_team_size(client):
    """
    Test Case: TC-FR-016-03
    Requirement: FR-16
    Feature: F004
    API endpoint rejects solo tournament with team_size
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)
    request_payload = {
        "name": "Invalid Solo Tournament",
        "rank_tier": "BEGINNER",
        "region": "NA",
        "capacity": 16,
        "format": "Single Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": False,
        "team_size": 3  # Should not be specified for solo
    }

    # Act
    response = client.post("/api/tournaments/", json=request_payload)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "solo" in data["detail"].lower()


def test_api_create_tournament_team_size_out_of_range(client):
    """
    Test Case: TC-FR-016-01 (API level)
    Requirement: FR-16
    Feature: F004
    API endpoint validates team_size range (2-5)
    """
    # Arrange
    future_time = datetime.now() + timedelta(days=30)

    # Test team_size too small
    request_payload_small = {
        "name": "Team Tournament Small",
        "rank_tier": "INTERMEDIATE",
        "region": "EU",
        "capacity": 16,
        "format": "Double Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": True,
        "team_size": 1  # Below minimum of 2
    }

    # Act
    response1 = client.post("/api/tournaments/", json=request_payload_small)

    # Assert
    assert response1.status_code in [400, 422]
    data1 = response1.json()
    assert "detail" in data1

    # Test team_size too large
    request_payload_large = {
        "name": "Team Tournament Large",
        "rank_tier": "INTERMEDIATE",
        "region": "EU",
        "capacity": 16,
        "format": "Double Elimination",
        "start_time": future_time.isoformat(),
        "is_team_tournament": True,
        "team_size": 10  # Exceeds maximum of 5
    }

    # Act
    response2 = client.post("/api/tournaments/", json=request_payload_large)

    # Assert
    assert response2.status_code in [400, 422]
    data2 = response2.json()
    assert "detail" in data2
