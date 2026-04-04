// Feature: F001
// Scenario: SC001, SC002
// Tournaments Page

import React, { useState } from 'react';
import { TournamentList } from '../components/TournamentList';
import { useAllTournaments, useRegisterTournament } from '../hooks/useTournaments';

/**
 * Feature: F001, F004
 * Scenario: SC001, SC002, SC007
 * Main tournaments page with registration flow and all tournaments display
 */
export const TournamentsPage: React.FC = () => {
  // TODO: Replace with actual player context/auth
  const [currentPlayerId] = useState(1);

  const { data, isLoading } = useAllTournaments();
  const registerMutation = useRegisterTournament();

  const handleJoinTournament = async (tournamentId: number) => {
    try {
      const result = await registerMutation.mutateAsync({
        playerId: currentPlayerId,
        request: { tournament_id: tournamentId },
      });

      if (result.status === 'success') {
        alert(`Success: ${result.message}`);
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      alert('Failed to register for tournament');
      console.error(error);
    }
  };

  return (
    <div className="tournaments-page">
      <h1>Tournaments</h1>
      <TournamentList
        tournaments={data?.tournaments || []}
        onJoinTournament={handleJoinTournament}
        isLoading={isLoading}
      />
    </div>
  );
};
