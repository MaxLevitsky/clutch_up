# Feature: FR-006a - Allow team creation through website
# Test Suite: Player Seeding Integration Tests
# Traceability: TC-FR-006a-01, TC-FR-006a-02, TC-FR-006a-03, TC-FR-006a-04

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.player import Player, RankTier
from app.main import seed_default_player


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_seeding.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_seed_default_player_creates_player(test_db, monkeypatch):
    """
    TC-FR-006a-01: Verify default player creation
    Given: Empty database
    When: seed_default_player() is called
    Then: Player with id=1 is created with correct attributes
    """
    # Mock SessionLocal to use test database
    monkeypatch.setattr("app.main.SessionLocal", TestingSessionLocal)

    # Execute seeding
    seed_default_player()

    # Verify player was created
    db = TestingSessionLocal()
    try:
        player = db.query(Player).filter(Player.id == 1).first()
        assert player is not None, "Default player should be created"
        assert player.username == 'demo_player'
        assert player.email == 'demo@clutchup.local'
        assert player.region == 'NA'
        assert player.rank == RankTier.BEGINNER
        assert player.account_status == 'ACTIVE'
        assert player.progression_level == 1
    finally:
        db.close()


def test_seed_default_player_idempotent(test_db, monkeypatch):
    """
    TC-FR-006a-02: Verify seeding is idempotent
    Given: Default player already exists
    When: seed_default_player() is called again
    Then: No duplicate players are created
    """
    # Mock SessionLocal to use test database
    monkeypatch.setattr("app.main.SessionLocal", TestingSessionLocal)

    # First seeding
    seed_default_player()

    # Second seeding (should skip)
    seed_default_player()

    # Verify only one player exists
    db = TestingSessionLocal()
    try:
        player_count = db.query(Player).filter(Player.id == 1).count()
        assert player_count == 1, "Should have exactly one default player"
    finally:
        db.close()


def test_seed_default_player_does_not_overwrite(test_db, monkeypatch):
    """
    TC-FR-006a-03: Verify existing player is not modified
    Given: Player with id=1 exists with custom data
    When: seed_default_player() is called
    Then: Existing player data is preserved
    """
    # Mock SessionLocal to use test database
    monkeypatch.setattr("app.main.SessionLocal", TestingSessionLocal)

    # Create custom player with id=1
    db = TestingSessionLocal()
    try:
        custom_player = Player(
            id=1,
            username='custom_user',
            email='custom@example.com',
            region='EU',
            rank=RankTier.INTERMEDIATE,
            account_status='ACTIVE',
            progression_level=5
        )
        db.add(custom_player)
        db.commit()
    finally:
        db.close()

    # Attempt seeding
    seed_default_player()

    # Verify custom player data is preserved
    db = TestingSessionLocal()
    try:
        player = db.query(Player).filter(Player.id == 1).first()
        assert player.username == 'custom_user', "Username should be preserved"
        assert player.email == 'custom@example.com', "Email should be preserved"
        assert player.region == 'EU', "Region should be preserved"
        assert player.rank == RankTier.INTERMEDIATE, "Rank should be preserved"
        assert player.progression_level == 5, "Progression level should be preserved"
    finally:
        db.close()


def test_seed_allows_team_creation(test_db, monkeypatch):
    """
    TC-FR-006a-04: Verify team creation succeeds after seeding
    Given: Default player has been seeded
    When: Attempting to create a team with player_id=1
    Then: Team creation succeeds without "Player not found" error
    """
    from app.models.team import Team

    # Mock SessionLocal to use test database
    monkeypatch.setattr("app.main.SessionLocal", TestingSessionLocal)

    # Seed default player
    seed_default_player()

    # Attempt to create team with owner_id=1
    db = TestingSessionLocal()
    try:
        team = Team(
            name='Test Team',
            owner_id=1,
            badge='shield'
        )
        db.add(team)
        db.commit()
        db.refresh(team)

        # Verify team was created successfully
        assert team.id is not None, "Team should be created with an ID"
        assert team.owner_id == 1, "Team should reference owner id=1"
    finally:
        db.close()


def test_seed_handles_database_errors(test_db, monkeypatch):
    """
    Integration Test: Verify seeding handles database errors gracefully
    Given: Database connection fails during seeding
    When: seed_default_player() is called
    Then: Exception is raised and transaction is rolled back
    """
    from unittest.mock import MagicMock

    # Create a mock session that raises an exception on commit
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_session.commit.side_effect = Exception("Database error")

    mock_session_local = MagicMock(return_value=mock_session)
    monkeypatch.setattr("app.main.SessionLocal", mock_session_local)

    # Verify exception is raised
    with pytest.raises(Exception, match="Database error"):
        seed_default_player()

    # Verify rollback was called
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
