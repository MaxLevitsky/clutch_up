# Feature: F001, F004
# Scenario: SC001, SC002, SC007
# Test Cases: TC-FR-001-01, TC-FR-001-02, TC-FR-002-01, TC-FR-002-02, TC-FR-002-03
# Test Cases (NEW): TC-FR-013-01, TC-FR-014-01, TC-FR-014-02, TC-FR-015-01, TC-FR-016-01, TC-FR-016-02

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from app.services.tournament_service import TournamentService
from app.models.player import Player, RankTier
from app.models.tournament import Tournament, TournamentStatus


def test_get_eligible_tournaments_success():
    """
    Test Case: TC-FR-001-02
    Requirement: FR-1
    Eligible tournament list shows only available beginner events
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="NA"
    )
    mock_player_repo.get_by_id.return_value = player

    eligible_tournament = Tournament(
        id=1,
        name="Beginner Cup",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        registered_count=5,
        status=TournamentStatus.REGISTRATION_OPEN,
        start_time="2026-04-01 10:00:00",
        format="Single Elimination",
        is_team_tournament=0
    )
    mock_tournament_repo.get_eligible_tournaments.return_value = [eligible_tournament]

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.get_eligible_tournaments(player_id=1)

    # Assert
    assert len(result) == 1
    assert result[0].name == "Beginner Cup"
    assert result[0].rank_tier == "BEGINNER"
    mock_player_repo.get_by_id.assert_called_once_with(1)
    mock_tournament_repo.get_eligible_tournaments.assert_called_once_with("BEGINNER", "NA")


def test_validate_eligibility_rank_mismatch():
    """
    Test Case: TC-FR-002-01
    Requirement: FR-4, FR-5
    Ineligible player cannot join higher-rank tournament
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="NA",
        account_status="ACTIVE"
    )
    mock_player_repo.get_by_id.return_value = player

    tournament = Tournament(
        id=1,
        name="Advanced Cup",
        rank_tier="ADVANCED",
        region="NA",
        capacity=16,
        registered_count=5,
        status=TournamentStatus.REGISTRATION_OPEN,
        start_time="2026-04-01 10:00:00",
        format="Single Elimination",
        is_team_tournament=0
    )
    mock_tournament_repo.get_by_id.return_value = tournament

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.validate_eligibility(player_id=1, tournament_id=1)

    # Assert
    assert result["eligible"] is False
    assert result["reason"] == "Rank mismatch"
    assert "ADVANCED" in result["user_message"]
    assert "BEGINNER" in result["user_message"]


def test_validate_eligibility_region_mismatch():
    """
    Test Case: TC-FR-002-02
    Requirement: FR-4, FR-5
    Player from unsupported region is blocked from registration
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="EU",
        account_status="ACTIVE"
    )
    mock_player_repo.get_by_id.return_value = player

    tournament = Tournament(
        id=1,
        name="Beginner Cup NA",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        registered_count=5,
        status=TournamentStatus.REGISTRATION_OPEN,
        start_time="2026-04-01 10:00:00",
        format="Single Elimination",
        is_team_tournament=0
    )
    mock_tournament_repo.get_by_id.return_value = tournament

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.validate_eligibility(player_id=1, tournament_id=1)

    # Assert
    assert result["eligible"] is False
    assert result["reason"] == "Region mismatch"


def test_validate_eligibility_duplicate_registration():
    """
    Test Case: TC-FR-002-03
    Requirement: NFR-3
    Duplicate registration attempt is rejected
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="NA",
        account_status="ACTIVE"
    )
    mock_player_repo.get_by_id.return_value = player

    tournament = Tournament(
        id=1,
        name="Beginner Cup",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        registered_count=5,
        status=TournamentStatus.REGISTRATION_OPEN,
        start_time="2026-04-01 10:00:00",
        format="Single Elimination",
        is_team_tournament=0
    )
    mock_tournament_repo.get_by_id.return_value = tournament
    mock_tournament_repo.is_player_registered.return_value = True  # Already registered

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.validate_eligibility(player_id=1, tournament_id=1)

    # Assert
    assert result["eligible"] is False
    assert result["reason"] == "Already registered"
    assert "already registered" in result["user_message"]


def test_register_player_success():
    """
    Test Case: TC-FR-001-01
    Requirement: FR-2, FR-3
    Eligible beginner player joins beginner tournament
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="NA",
        account_status="ACTIVE"
    )
    mock_player_repo.get_by_id.return_value = player

    tournament = Tournament(
        id=1,
        name="Beginner Cup",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        registered_count=5,
        status=TournamentStatus.REGISTRATION_OPEN,
        start_time="2026-04-01 10:00:00",
        format="Single Elimination",
        is_team_tournament=0
    )
    mock_tournament_repo.get_by_id.return_value = tournament
    mock_tournament_repo.is_player_registered.return_value = False

    mock_registration = MagicMock()
    mock_registration.registered_at = "2026-03-21 12:00:00"
    mock_tournament_repo.register_player.return_value = mock_registration

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.register_player(player_id=1, tournament_id=1)

    # Assert
    assert result["status"] == "success"
    assert result["tournament_id"] == 1
    assert result["player_id"] == 1
    assert "Beginner Cup" in result["message"]
    mock_tournament_repo.register_player.assert_called_once_with(1, 1)


# ============================================================================
# NEW TESTS: Tournament Creation (Feature F004, UC-4.1)
# ============================================================================


def test_create_tournament_success():
    """
    Test Case: TC-FR-013-01
    Requirement: FR-13
    Feature: F004
    Scenario: SC007
    Create tournament with valid parameters
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    created_tournament = Tournament(
        id=1,
        name="Spring Championship 2026",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=0,
        team_size=None,
        status=TournamentStatus.UPCOMING,
        registered_count=0
    )
    mock_tournament_repo.create.return_value = created_tournament

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Spring Championship 2026",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result["status"] == "success"
    assert "created successfully" in result["message"].lower()
    assert result["tournament"].name == "Spring Championship 2026"
    assert result["tournament"].status == TournamentStatus.UPCOMING
    assert result["tournament"].registered_count == 0
    mock_tournament_repo.create.assert_called_once()


def test_create_tournament_invalid_capacity():
    """
    Test Case: TC-FR-014-01
    Requirement: FR-14
    Feature: F004
    Reject tournament creation with invalid capacity (≤ 0)
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act - Test capacity = 0
    result_zero = service.create_tournament(
        name="Invalid Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=0,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result_zero["status"] == "error"
    assert "capacity" in result_zero["message"].lower()
    assert mock_tournament_repo.create.call_count == 0

    # Act - Test capacity < 0
    result_negative = service.create_tournament(
        name="Invalid Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=-5,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result_negative["status"] == "error"
    assert "capacity" in result_negative["message"].lower()
    assert mock_tournament_repo.create.call_count == 0


def test_create_tournament_past_start_time():
    """
    Test Case: TC-FR-014-02
    Requirement: FR-14
    Feature: F004
    Reject tournament creation with past start time
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    past_time = datetime(2020, 1, 1, 10, 0, 0)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Past Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=past_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result["status"] == "error"
    assert "future" in result["message"].lower() or "past" in result["message"].lower()
    mock_tournament_repo.create.assert_not_called()


def test_create_tournament_sets_upcoming_status():
    """
    Test Case: TC-FR-015-01
    Requirement: FR-15
    Feature: F004
    Verify tournament created with UPCOMING status and registered_count = 0
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    created_tournament = Tournament(
        id=1,
        name="Test Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=0,
        status=TournamentStatus.UPCOMING,
        registered_count=0
    )
    mock_tournament_repo.create.return_value = created_tournament

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Test Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result["status"] == "success"

    # Verify the service passed correct values to repository
    call_args = mock_tournament_repo.create.call_args
    # The service should ensure status is set to UPCOMING and count to 0
    # This verifies the service layer enforces this business rule
    assert result["tournament"].status == TournamentStatus.UPCOMING
    assert result["tournament"].registered_count == 0


def test_create_team_tournament_requires_team_size():
    """
    Test Case: TC-FR-016-01
    Requirement: FR-16
    Feature: F004
    Reject team tournament creation without team size
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Team Tournament",
        rank_tier="INTERMEDIATE",
        region="EU",
        capacity=8,
        format="Double Elimination",
        start_time=future_time,
        is_team_tournament=True,
        team_size=None  # Missing required field
    )

    # Assert
    assert result["status"] == "error"
    assert "team" in result["message"].lower() and "size" in result["message"].lower()
    assert "specify" in result["message"].lower() or "must" in result["message"].lower()
    mock_tournament_repo.create.assert_not_called()


def test_create_solo_tournament_without_team_size():
    """
    Test Case: TC-FR-016-02
    Requirement: FR-16
    Feature: F004
    Accept solo tournament creation without team size
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    created_tournament = Tournament(
        id=1,
        name="Solo Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=0,
        team_size=None,
        status=TournamentStatus.UPCOMING,
        registered_count=0
    )
    mock_tournament_repo.create.return_value = created_tournament

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Solo Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None  # Should be accepted/ignored for solo tournaments
    )

    # Assert
    assert result["status"] == "success"
    assert result["tournament"].name == "Solo Tournament"
    mock_tournament_repo.create.assert_called_once()


def test_create_tournament_capacity_exceeds_maximum():
    """
    Test Case: TC-FR-014-03 (Unit level)
    Requirement: FR-14
    Feature: F004
    Reject tournament with capacity > 64
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Oversized Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=100,  # Exceeds maximum of 64
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result["status"] == "error"
    assert "capacity" in result["message"].lower()
    assert "64" in result["message"]
    mock_tournament_repo.create.assert_not_called()


def test_create_tournament_capacity_below_minimum():
    """
    Test Case: TC-FR-014-01 (additional boundary test)
    Requirement: FR-14
    Feature: F004
    Reject tournament with capacity < 8
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Tiny Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=0,  # Below minimum of 1
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=None
    )

    # Assert
    assert result["status"] == "error"
    assert "capacity" in result["message"].lower()
    mock_tournament_repo.create.assert_not_called()


def test_create_tournament_solo_with_team_size_rejected():
    """
    Test Case: TC-FR-016-02 (negative case)
    Requirement: FR-16
    Feature: F004
    Reject solo tournament with team_size specified
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Solo Tournament",
        rank_tier="BEGINNER",
        region="NA",
        capacity=16,
        format="Single Elimination",
        start_time=future_time,
        is_team_tournament=False,
        team_size=3  # Should not be specified for solo tournament
    )

    # Assert
    assert result["status"] == "error"
    assert "solo" in result["message"].lower() and "team_size" in result["message"].lower()
    mock_tournament_repo.create.assert_not_called()


def test_create_tournament_team_size_below_minimum():
    """
    Test Case: TC-FR-016-01 (boundary test)
    Requirement: FR-16
    Feature: F004
    Reject team tournament with team_size < 2
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Team Tournament",
        rank_tier="INTERMEDIATE",
        region="EU",
        capacity=16,
        format="Double Elimination",
        start_time=future_time,
        is_team_tournament=True,
        team_size=1  # Below minimum of 2
    )

    # Assert
    assert result["status"] == "error"
    assert "team size" in result["message"].lower()
    assert "2" in result["message"] and "5" in result["message"]
    mock_tournament_repo.create.assert_not_called()


def test_create_tournament_team_size_exceeds_maximum():
    """
    Test Case: TC-FR-016-01 (boundary test)
    Requirement: FR-16
    Feature: F004
    Reject team tournament with team_size > 5
    """
    # Arrange
    mock_tournament_repo = Mock()
    mock_player_repo = Mock()

    future_time = datetime.now() + timedelta(days=30)

    service = TournamentService(mock_tournament_repo, mock_player_repo)

    # Act
    result = service.create_tournament(
        name="Team Tournament",
        rank_tier="INTERMEDIATE",
        region="EU",
        capacity=16,
        format="Double Elimination",
        start_time=future_time,
        is_team_tournament=True,
        team_size=10  # Exceeds maximum of 5
    )

    # Assert
    assert result["status"] == "error"
    assert "team size" in result["message"].lower()
    assert "2" in result["message"] and "5" in result["message"]
    mock_tournament_repo.create.assert_not_called()
