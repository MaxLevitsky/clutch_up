// Feature: F002
// Teams Page

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TeamCreation } from '../components/TeamCreation';
import { useCreateTeam, useMyTeams, useAcceptInvite } from '../hooks/useTeams';
import { useAuth } from '../context/AuthContext';

export const TeamsPage: React.FC = () => {
  const { currentPlayer } = useAuth();
  const currentPlayerId = currentPlayer!.id;
  const navigate = useNavigate();

  const { data: myTeamsData, isLoading: teamsLoading } = useMyTeams(currentPlayerId);
  const createTeamMutation = useCreateTeam();
  const acceptInviteMutation = useAcceptInvite();

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [inviteToken, setInviteToken] = useState('');

  const handleCreateTeam = async (name: string, badge?: string) => {
    try {
      const result = await createTeamMutation.mutateAsync({
        ownerId: currentPlayerId,
        data: { name, badge },
      });
      if (result.status === 'success') {
        alert(`Team "${result.team.name}" created!`);
        setShowCreateForm(false);
        navigate(`/teams/${result.team.id}`);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create team');
    }
  };

  const handleJoinTeam = async () => {
    if (!inviteToken.trim()) return;
    try {
      const result = await acceptInviteMutation.mutateAsync({
        token: inviteToken.trim(),
        playerId: currentPlayerId,
      });
      if (result.status === 'success') {
        alert(result.message);
        setInviteToken('');
        navigate(`/teams/${result.team_id}`);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Invalid invite token');
    }
  };

  const teams: any[] = myTeamsData?.teams || [];

  return (
    <div className="teams-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Teams</h1>
        <button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? 'Cancel' : '+ Create Team'}
        </button>
      </div>

      {showCreateForm && (
        <TeamCreation
          onCreateTeam={handleCreateTeam}
          isLoading={createTeamMutation.isPending}
        />
      )}

      <div className="join-team-section" style={{ margin: '20px 0', padding: '16px', border: '1px solid #ddd', borderRadius: 8 }}>
        <h2>Join a Team</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            type="text"
            value={inviteToken}
            onChange={(e) => setInviteToken(e.target.value)}
            placeholder="Paste invite token"
            style={{ flex: 1 }}
          />
          <button
            onClick={handleJoinTeam}
            disabled={!inviteToken.trim() || acceptInviteMutation.isPending}
          >
            {acceptInviteMutation.isPending ? 'Joining...' : 'Join'}
          </button>
        </div>
      </div>

      <div className="my-teams-section">
        <h2>My Teams</h2>
        {teamsLoading ? (
          <p>Loading...</p>
        ) : teams.length === 0 ? (
          <p>You are not a member of any team yet.</p>
        ) : (
          <div style={{ display: 'grid', gap: 12 }}>
            {teams.map((team) => (
              <div
                key={team.id}
                onClick={() => navigate(`/teams/${team.id}`)}
                style={{
                  padding: 16,
                  border: '1px solid #ddd',
                  borderRadius: 8,
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <strong>{team.name}</strong>
                  {team.badge && <span style={{ marginLeft: 8, color: '#666' }}>🏅 {team.badge}</span>}
                  {team.owner_id === currentPlayerId && (
                    <span style={{ marginLeft: 8, fontSize: 12, color: '#888' }}>(Owner)</span>
                  )}
                </div>
                <span style={{ color: '#666' }}>→</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
