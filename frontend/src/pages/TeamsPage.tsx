// Feature: F002
// Scenario: SC003
// Teams Page

import React from 'react';
import { TeamCreation } from '../components/TeamCreation';
import { useCreateTeam } from '../hooks/useTeams';
import { useAuth } from '../context/AuthContext';

/**
 * Feature: F002
 * Scenario: SC003
 * Main teams page with creation flow
 */
export const TeamsPage: React.FC = () => {
  const { currentPlayer } = useAuth();
  const currentPlayerId = currentPlayer!.id;

  const createTeamMutation = useCreateTeam();

  const handleCreateTeam = async (name: string, badge?: string) => {
    try {
      const result = await createTeamMutation.mutateAsync({
        ownerId: currentPlayerId,
        data: { name, badge },
      });

      if (result.status === 'success') {
        alert(`Team "${result.team.name}" created successfully!`);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create team');
      console.error(error);
    }
  };

  return (
    <div className="teams-page">
      <h1>Teams</h1>
      <TeamCreation
        onCreateTeam={handleCreateTeam}
        isLoading={createTeamMutation.isPending}
      />
    </div>
  );
};
