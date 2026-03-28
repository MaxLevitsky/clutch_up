# Feature: F002
# Scenario: SC003, SC004
# Team Repository

from sqlalchemy.orm import Session
from app.models.team import Team
from app.models.team_membership import TeamMembership, MemberRole
from app.models.team_invite import TeamInvite, InviteStatus
from typing import Optional, List
from datetime import datetime, timedelta
import secrets


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, team_id: int) -> Optional[Team]:
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_by_name(self, name: str) -> Optional[Team]:
        return self.db.query(Team).filter(Team.name == name).first()

    def create(self, name: str, owner_id: int, badge: Optional[str] = None) -> Team:
        team = Team(name=name, owner_id=owner_id, badge=badge)
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)

        # Add owner as team member
        membership = TeamMembership(
            team_id=team.id,
            player_id=owner_id,
            role=MemberRole.OWNER
        )
        self.db.add(membership)
        self.db.commit()

        return team

    def create_invite(self, team_id: int, invited_by: int, expires_in_days: int = 7) -> TeamInvite:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        invite = TeamInvite(
            team_id=team_id,
            token=token,
            invited_by=invited_by,
            expires_at=expires_at
        )
        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)
        return invite

    def get_invite_by_token(self, token: str) -> Optional[TeamInvite]:
        return self.db.query(TeamInvite).filter(TeamInvite.token == token).first()

    def accept_invite(self, token: str, player_id: int) -> bool:
        invite = self.get_invite_by_token(token)
        if not invite or invite.status != InviteStatus.PENDING:
            return False

        if invite.expires_at < datetime.utcnow():
            invite.status = InviteStatus.EXPIRED
            self.db.commit()
            return False

        # Add player to team
        membership = TeamMembership(
            team_id=invite.team_id,
            player_id=player_id,
            role=MemberRole.MEMBER
        )
        self.db.add(membership)

        invite.status = InviteStatus.ACCEPTED
        invite.used_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_team_members(self, team_id: int) -> List[TeamMembership]:
        return self.db.query(TeamMembership).filter(TeamMembership.team_id == team_id).all()

    def get_team_member_count(self, team_id: int) -> int:
        return self.db.query(TeamMembership).filter(TeamMembership.team_id == team_id).count()

    def revoke_invite(self, token: str) -> bool:
        invite = self.get_invite_by_token(token)
        if invite and invite.status == InviteStatus.PENDING:
            invite.status = InviteStatus.REVOKED
            self.db.commit()
            return True
        return False
