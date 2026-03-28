# Feature: F001
# Scenario: SC001, SC002
# Test Cases: TC-FR-001-01, TC-FR-001-02, TC-FR-002-01, TC-FR-002-02, TC-FR-002-03

import pytest
from unittest.mock import Mock, MagicMock
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
