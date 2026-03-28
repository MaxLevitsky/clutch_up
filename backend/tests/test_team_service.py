# Feature: F002
# Scenario: SC003, SC004
# Test Cases: TC-FR-003-01, TC-FR-003-02, TC-FR-003-03, TC-FR-004-01, TC-FR-004-02

import pytest
from unittest.mock import Mock
from app.services.team_service import TeamService
from app.models.player import Player, RankTier
from app.models.team import Team


def test_create_team_success():
    """
    Test Case: TC-FR-003-01
    Requirement: FR-6
    User creates a team and sends invite
    """
    # Arrange
    mock_team_repo = Mock()
    mock_player_repo = Mock()
    mock_tournament_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="NA"
    )
    mock_player_repo.get_by_id.return_value = player
    mock_team_repo.get_by_name.return_value = None  # Name is unique

    team = Team(
        id=1,
        name="Test Team",
        badge="shield",
        owner_id=1
    )
    mock_team_repo.create.return_value = team

    service = TeamService(mock_team_repo, mock_player_repo, mock_tournament_repo)

    # Act
    result = service.create_team(name="Test Team", owner_id=1, badge="shield")

    # Assert
    assert result["status"] == "success"
    assert result["team"].name == "Test Team"
    mock_team_repo.create.assert_called_once_with("Test Team", 1, "shield")


def test_create_team_duplicate_name():
    """
    Test Case: TC-FR-003-03
    Requirement: FR-6
    Team name must be unique according to system rules
    """
    # Arrange
    mock_team_repo = Mock()
    mock_player_repo = Mock()
    mock_tournament_repo = Mock()

    player = Player(
        id=1,
        username="testplayer",
        email="test@example.com",
        rank=RankTier.BEGINNER,
        region="NA"
    )
    mock_player_repo.get_by_id.return_value = player

    existing_team = Team(
        id=2,
        name="Existing Team",
        badge="star",
        owner_id=2
    )
    mock_team_repo.get_by_name.return_value = existing_team  # Name already exists

    service = TeamService(mock_team_repo, mock_player_repo, mock_tournament_repo)

    # Act
    result = service.create_team(name="Existing Team", owner_id=1, badge="shield")

    # Assert
    assert result["status"] == "error"
    assert "already exists" in result["message"]


def test_accept_invite_success():
    """
    Test Case: TC-FR-003-02
    Requirement: FR-7
    Invited friend joins team successfully
    """
    # Arrange
    mock_team_repo = Mock()
    mock_player_repo = Mock()
    mock_tournament_repo = Mock()

    player = Player(
        id=2,
        username="invitedplayer",
        email="invited@example.com",
        rank=RankTier.BEGINNER,
        region="NA"
    )
    mock_player_repo.get_by_id.return_value = player

    mock_invite = Mock()
    mock_invite.team_id = 1
    mock_team_repo.get_invite_by_token.return_value = mock_invite

    team = Team(
        id=1,
        name="Test Team",
        badge="shield",
        owner_id=1
    )
    mock_team_repo.get_by_id.return_value = team
    mock_team_repo.accept_invite.return_value = True

    service = TeamService(mock_team_repo, mock_player_repo, mock_tournament_repo)

    # Act
    result = service.accept_invite(token="test_token", player_id=2)

    # Assert
    assert result["status"] == "success"
    assert "Test Team" in result["message"]
    mock_team_repo.accept_invite.assert_called_once_with("test_token", 2)


def test_validate_team_tournament_eligibility_insufficient_roster():
    """
    Test Case: TC-FR-004-02
    Requirement: FR-9
    Team with insufficient roster cannot join tournament
    """
    # Arrange
    mock_team_repo = Mock()
    mock_player_repo = Mock()
    mock_tournament_repo = Mock()

    team = Team(
        id=1,
        name="Small Team",
        badge="shield",
        owner_id=1
    )
    mock_team_repo.get_by_id.return_value = team
    mock_team_repo.get_team_member_count.return_value = 2  # Only 2 members

    tournament = Mock()
    tournament.id = 1
    tournament.is_team_tournament = 1
    tournament.team_size = 5  # Requires 5 members
    tournament.registered_count = 0
    tournament.capacity = 10
    mock_tournament_repo.get_by_id.return_value = tournament

    service = TeamService(mock_team_repo, mock_player_repo, mock_tournament_repo)

    # Act
    result = service.validate_team_tournament_eligibility(team_id=1, tournament_id=1)

    # Assert
    assert result["eligible"] is False
    assert result["reason"] == "Insufficient team size"
    assert "at least 5 members" in result["user_message"]


def test_register_team_for_tournament_success():
    """
    Test Case: TC-FR-004-01
    Requirement: FR-9, FR-10
    Eligible team joins team tournament
    """
    # Arrange
    mock_team_repo = Mock()
    mock_player_repo = Mock()
    mock_tournament_repo = Mock()

    team = Team(
        id=1,
        name="Full Team",
        badge="shield",
        owner_id=1
    )
    mock_team_repo.get_by_id.return_value = team
    mock_team_repo.get_team_member_count.return_value = 5

    tournament = Mock()
    tournament.id = 1
    tournament.name = "Team Championship"
    tournament.is_team_tournament = 1
    tournament.team_size = 5
    tournament.registered_count = 0
    tournament.capacity = 10
    mock_tournament_repo.get_by_id.return_value = tournament

    mock_members = [Mock(player_id=i) for i in range(1, 6)]
    mock_team_repo.get_team_members.return_value = mock_members

    service = TeamService(mock_team_repo, mock_player_repo, mock_tournament_repo)

    # Act
    result = service.register_team_for_tournament(team_id=1, tournament_id=1, owner_id=1)

    # Assert
    assert result["status"] == "success"
    assert result["roster_locked"] is True
    assert result["member_count"] == 5
    assert "Team Championship" in result["message"]
