// Feature: F001
// Scenario: SC001
// Tournament List Component

import React from 'react';
import { Link } from 'react-router-dom';
import { Tournament } from '../services/api/tournaments';

interface TournamentListProps {
  tournaments: Tournament[];
  onJoinTournament: (tournamentId: number) => void;
  isLoading?: boolean;
}

/**
 * Feature: F001
 * Scenario: SC001
 * Requirement: FR-1
 * Display eligible tournaments
 */
export const TournamentList: React.FC<TournamentListProps> = ({
  tournaments,
  onJoinTournament,
  isLoading,
}) => {
  if (isLoading) {
    return <div className="loading">Loading tournaments...</div>;
  }

  if (!tournaments || tournaments.length === 0) {
    return <div className="no-tournaments">No eligible tournaments available.</div>;
  }

  return (
    <div className="tournament-list">
      <h2>Available Tournaments</h2>
      {tournaments.map((tournament) => (
        <div key={tournament.id} className="tournament-card">
          <h3><Link to={`/tournaments/${tournament.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>{tournament.name}</Link></h3>
          <div className="tournament-details">
            <p>
              <strong>Rank:</strong> {tournament.rank_tier}
            </p>
            <p>
              <strong>Region:</strong> {tournament.region}
            </p>
            <p>
              <strong>Format:</strong> {tournament.format}
            </p>
            <p>
              <strong>Start Time:</strong>{' '}
              {new Date(tournament.start_time).toLocaleString()}
            </p>
            <p>
              <strong>Capacity:</strong> {tournament.registered_count} /{' '}
              {tournament.capacity}
            </p>
            <p>
              <strong>Status:</strong> {tournament.status}
            </p>
            <p>
              <strong>Created by:</strong> {tournament.creator_username ?? '—'}
            </p>
          </div>
          <button
            onClick={() => onJoinTournament(tournament.id)}
            disabled={
              !['REGISTRATION_OPEN', 'UPCOMING'].includes(tournament.status) ||
              tournament.registered_count >= tournament.capacity
            }
            className="join-button"
          >
            Join Tournament
          </button>
        </div>
      ))}
    </div>
  );
};
