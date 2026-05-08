# Feature: F002
# Scenario: SC003
# Requirement: NFR-2
# Test Cases: TC-NFR-002-01, TC-NFR-002-02, TC-NFR-002-03

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.player import Player, RankTier
from app.models.team import Team
from app.models.team_membership import TeamMembership, MemberRole
from app.models.team_invite import TeamInvite, InviteStatus

TEST_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(test_db):
    return TestClient(app)


def _seed_team_and_invite(token: str, expired: bool = False) -> dict:
    """Insert owner, team, pending invite, and an invitee. Returns their IDs."""
    db = TestingSessionLocal()
    try:
        owner = Player(
            username=f"owner_{token[:6]}",
            email=f"owner_{token[:6]}@test.com",
            region="NA", rank=RankTier.BEGINNER,
            account_status="ACTIVE", progression_level=1,
        )
        db.add(owner)
        db.flush()

        team = Team(name=f"Team {token[:6]}", owner_id=owner.id, badge="shield")
        db.add(team)
        db.flush()

        db.add(TeamMembership(team_id=team.id, player_id=owner.id, role=MemberRole.OWNER))

        expires = (datetime.utcnow() - timedelta(days=1)) if expired else (datetime.utcnow() + timedelta(days=7))
        invite = TeamInvite(
            team_id=team.id,
            invited_by=owner.id,
            token=token,
            status=InviteStatus.PENDING,
            expires_at=expires,
        )
        db.add(invite)

        invitee = Player(
            username=f"inv_{token[:6]}",
            email=f"inv_{token[:6]}@test.com",
            region="NA", rank=RankTier.BEGINNER,
            account_status="ACTIVE", progression_level=1,
        )
        db.add(invitee)
        db.commit()
        return {"owner_id": owner.id, "team_id": team.id, "invitee_id": invitee.id}
    finally:
        db.close()


# ─── TC-NFR-002-01 ────────────────────────────────────────────────────────────

def test_tampered_token_rejected(client, test_db):
    """
    TC-NFR-002-01 — Requirement: NFR-2
    Accepting with a token that never existed must be rejected.
    """
    data = _seed_team_and_invite("real-token-aaa")

    response = client.post(
        f"/api/teams/invites/TAMPERED-TOKEN-XYZ/accept?player_id={data['invitee_id']}"
    )
    assert response.status_code == 400


def test_partially_modified_token_rejected(client, test_db):
    """
    TC-NFR-002-01 variant — Modifying one character of a real token must fail.
    """
    data = _seed_team_and_invite("real-token-bbb")

    # Flip one character
    response = client.post(
        f"/api/teams/invites/real-token-BBB/accept?player_id={data['invitee_id']}"
    )
    assert response.status_code == 400


# ─── TC-NFR-002-02 ────────────────────────────────────────────────────────────

def test_revoked_invite_cannot_be_accepted(client, test_db):
    """
    TC-NFR-002-02 — Requirement: NFR-2
    Revoked invite links must be rejected even if token is valid.
    """
    data = _seed_team_and_invite("real-token-ccc")
    token = "real-token-ccc"

    # Owner revokes the invite
    revoke = client.delete(f"/api/teams/invites/{token}/revoke?owner_id={data['owner_id']}")
    assert revoke.status_code == 200
    assert revoke.json()["status"] == "success"

    # Invitee tries to use revoked invite
    accept = client.post(f"/api/teams/invites/{token}/accept?player_id={data['invitee_id']}")
    assert accept.status_code == 400


def test_accepted_invite_cannot_be_reused(client, test_db):
    """
    TC-NFR-002-02 variant — Once accepted, invite cannot be used again.
    """
    data = _seed_team_and_invite("real-token-ddd")
    token = "real-token-ddd"

    # First accept — should succeed
    first = client.post(f"/api/teams/invites/{token}/accept?player_id={data['invitee_id']}")
    assert first.status_code == 200
    assert first.json()["status"] == "success"

    # Second accept — should be rejected (already ACCEPTED, not PENDING)
    second_db = TestingSessionLocal()
    try:
        second_invitee = Player(
            username="second_inv", email="second_inv@test.com",
            region="NA", rank=RankTier.BEGINNER, account_status="ACTIVE", progression_level=1,
        )
        second_db.add(second_invitee)
        second_db.commit()
        second_id = second_invitee.id
    finally:
        second_db.close()

    second = client.post(f"/api/teams/invites/{token}/accept?player_id={second_id}")
    assert second.status_code == 400


# ─── TC-NFR-002-03 ────────────────────────────────────────────────────────────

def test_expired_invite_cannot_be_accepted(client, test_db):
    """
    TC-NFR-002-03 — Expired invite tokens are rejected.
    """
    data = _seed_team_and_invite("real-token-eee", expired=True)

    accept = client.post(
        f"/api/teams/invites/real-token-eee/accept?player_id={data['invitee_id']}"
    )
    assert accept.status_code == 400


# ─── Positive baseline ────────────────────────────────────────────────────────

def test_valid_invite_accepted_successfully(client, test_db):
    """Positive control — valid pending invite must be accepted."""
    data = _seed_team_and_invite("real-token-fff")

    accept = client.post(
        f"/api/teams/invites/real-token-fff/accept?player_id={data['invitee_id']}"
    )
    assert accept.status_code == 200
    assert accept.json()["status"] == "success"
