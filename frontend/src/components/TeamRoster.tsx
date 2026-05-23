// Feature: F002
// Scenario: SC003
// Team Roster Component

import React from 'react';

interface TeamMember {
  player_id: number;
  player_username?: string;
  role: string;
  joined_at: string;
}

interface TeamRosterProps {
  teamName: string;
  members: TeamMember[];
  memberCount: number;
  isLoading?: boolean;
}

/**
 * Feature: F002
 * Scenario: SC003
 * Requirement: FR-8
 * Display current roster status
 */
export const TeamRoster: React.FC<TeamRosterProps> = ({
  teamName,
  members,
  memberCount,
  isLoading,
}) => {
  if (isLoading) {
    return <div className="loading">Loading roster...</div>;
  }

  return (
    <div className="team-roster">
      <h2>{teamName} Roster</h2>
      <p className="member-count">Total Members: {memberCount}</p>

      <div className="roster-list">
        {members && members.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Player</th>
                <th>Role</th>
                <th>Joined Date</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.player_id}>
                  <td>{member.player_username ?? `#${member.player_id}`}</td>
                  <td>{member.role}</td>
                  <td>{new Date(member.joined_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No members yet.</p>
        )}
      </div>
    </div>
  );
};
