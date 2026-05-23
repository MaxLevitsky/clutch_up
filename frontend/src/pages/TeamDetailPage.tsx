// Feature: F002
// Team Detail Page

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTeam, useCreateInvite, useRevokeInvite } from '../hooks/useTeams';
import { useAuth } from '../context/AuthContext';

export const TeamDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const teamId = Number(id);
  const navigate = useNavigate();
  const { currentPlayer } = useAuth();
  const currentPlayerId = currentPlayer!.id;

  const { data, isLoading, refetch } = useTeam(teamId);
  const createInviteMutation = useCreateInvite();
  const revokeInviteMutation = useRevokeInvite();

  const [inviteToken, setInviteToken] = useState<string | null>(null);

  if (isLoading) return <div className="loading">Loading team...</div>;
  if (!data || data.status === 'error') return <div>Team not found.</div>;

  const team = data.team;
  const members: any[] = data.members || [];
  const isOwner = team.owner_id === currentPlayerId;

  const handleGenerateInvite = async () => {
    try {
      const result = await createInviteMutation.mutateAsync({
        ownerId: currentPlayerId,
        data: { team_id: teamId },
      });
      if (result.status === 'success') {
        setInviteToken(result.invite.token);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create invite');
    }
  };

  const handleRevokeInvite = async () => {
    if (!inviteToken) return;
    try {
      await revokeInviteMutation.mutateAsync({ token: inviteToken, ownerId: currentPlayerId });
      setInviteToken(null);
      alert('Invite revoked');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to revoke invite');
    }
  };

  const copyToken = () => {
    if (inviteToken) {
      navigator.clipboard.writeText(inviteToken);
      alert('Token copied to clipboard!');
    }
  };

  return (
    <div className="team-detail-page">
      <button onClick={() => navigate('/teams')} style={{ marginBottom: 16 }}>
        ← Back to Teams
      </button>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <h1>{team.name}</h1>
        {team.badge && <span style={{ fontSize: 20 }}>🏅 {team.badge}</span>}
        {isOwner && (
          <span style={{ fontSize: 12, color: '#888', border: '1px solid #ccc', padding: '2px 8px', borderRadius: 12 }}>
            Owner
          </span>
        )}
      </div>

      {isOwner && (
        <div style={{ marginBottom: 24, padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
          <h2>Invite to Team</h2>
          {inviteToken ? (
            <div>
              <p style={{ marginBottom: 8 }}>Share this token with a player:</p>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <code
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    background: '#f5f5f5',
                    borderRadius: 4,
                    wordBreak: 'break-all',
                    fontSize: 13,
                  }}
                >
                  {inviteToken}
                </code>
                <button onClick={copyToken}>Copy</button>
                <button onClick={handleRevokeInvite} disabled={revokeInviteMutation.isPending}>
                  Revoke
                </button>
              </div>
            </div>
          ) : (
            <button onClick={handleGenerateInvite} disabled={createInviteMutation.isPending}>
              {createInviteMutation.isPending ? 'Creating...' : 'Generate Invite'}
            </button>
          )}
        </div>
      )}

      <div>
        <h2>Roster ({data.member_count})</h2>
        {members.length === 0 ? (
          <p>No members yet.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ddd' }}>
                <th style={{ textAlign: 'left', padding: '8px 12px' }}>Player</th>
                <th style={{ textAlign: 'left', padding: '8px 12px' }}>Role</th>
                <th style={{ textAlign: 'left', padding: '8px 12px' }}>Joined</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.player_id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px' }}>
                    {member.player_username ?? `#${member.player_id}`}
                    {member.player_id === currentPlayerId && (
                      <span style={{ marginLeft: 8, fontSize: 11, color: '#888' }}>(you)</span>
                    )}
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: 12,
                        fontSize: 12,
                        background: member.role === 'OWNER' ? '#e8f4fd' : '#f0f0f0',
                        color: member.role === 'OWNER' ? '#1a73e8' : '#555',
                      }}
                    >
                      {member.role === 'OWNER' ? 'Owner' : 'Member'}
                    </span>
                  </td>
                  <td style={{ padding: '8px 12px', color: '#666' }}>
                    {new Date(member.joined_at).toLocaleDateString('en-US')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
