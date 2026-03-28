// Feature: F002
// Scenario: SC003
// Team Creation Component

import React, { useState } from 'react';

interface TeamCreationProps {
  onCreateTeam: (name: string, badge?: string) => void;
  isLoading?: boolean;
}

/**
 * Feature: F002
 * Scenario: SC003
 * Requirement: FR-6
 * Team creation form
 */
export const TeamCreation: React.FC<TeamCreationProps> = ({
  onCreateTeam,
  isLoading,
}) => {
  const [teamName, setTeamName] = useState('');
  const [badge, setBadge] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (teamName.trim()) {
      onCreateTeam(teamName.trim(), badge.trim() || undefined);
      setTeamName('');
      setBadge('');
    }
  };

  return (
    <div className="team-creation">
      <h2>Create a Team</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="teamName">Team Name *</label>
          <input
            type="text"
            id="teamName"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            placeholder="Enter team name"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="badge">Badge (optional)</label>
          <input
            type="text"
            id="badge"
            value={badge}
            onChange={(e) => setBadge(e.target.value)}
            placeholder="Enter badge name"
            disabled={isLoading}
          />
        </div>

        <button type="submit" disabled={isLoading || !teamName.trim()}>
          {isLoading ? 'Creating...' : 'Create Team'}
        </button>
      </form>
    </div>
  );
};
