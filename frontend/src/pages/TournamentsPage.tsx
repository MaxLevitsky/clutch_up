// Feature: F001
// Scenario: SC001, SC002
// Tournaments Page

import React, { useMemo } from 'react';
import { TournamentList } from '../components/TournamentList';
import { useAllTournaments, useRegisterTournament } from '../hooks/useTournaments';
import { useAuth } from '../context/AuthContext';
import { Tournament } from '../services/api/tournaments';

const RANK_ORDER: Record<string, number> = {
  BEGINNER: 0,
  INTERMEDIATE: 1,
  ADVANCED: 2,
  EXPERT: 3,
};

const OPEN_STATUSES = new Set(['UPCOMING', 'REGISTRATION_OPEN', 'REGISTRATION_CLOSED']);

function sortByRankThenDate(a: Tournament, b: Tournament): number {
  const rankDiff = (RANK_ORDER[a.rank_tier] ?? 99) - (RANK_ORDER[b.rank_tier] ?? 99);
  if (rankDiff !== 0) return rankDiff;
  return new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
}

/**
 * Feature: F001, F004
 * Scenario: SC001, SC002, SC007
 * Main tournaments page with registration flow and all tournaments display
 */
export const TournamentsPage: React.FC = () => {
  const { currentPlayer } = useAuth();
  const currentPlayerId = currentPlayer!.id;

  const { data, isLoading } = useAllTournaments();
  const registerMutation = useRegisterTournament();

  const { openTournaments, activePastTournaments } = useMemo(() => {
    const all = data?.tournaments ?? [];
    const open = all.filter(t => OPEN_STATUSES.has(t.status)).sort(sortByRankThenDate);
    const activePast = all.filter(t => !OPEN_STATUSES.has(t.status)).sort(sortByRankThenDate);
    return { openTournaments: open, activePastTournaments: activePast };
  }, [data]);

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
        tournaments={openTournaments}
        onJoinTournament={handleJoinTournament}
        isLoading={isLoading}
        title="Available Tournaments"
        emptyMessage="No open tournaments available."
      />
      <TournamentList
        tournaments={activePastTournaments}
        onJoinTournament={handleJoinTournament}
        isLoading={false}
        title="Ongoing / Past Tournaments"
        emptyMessage="No ongoing or past tournaments."
      />
    </div>
  );
};
