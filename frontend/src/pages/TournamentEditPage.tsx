import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { TournamentForm } from '../components/TournamentForm';
import { useAllTournaments, useUpdateTournament } from '../hooks/useTournaments';
import { useAuth } from '../context/AuthContext';
import { TournamentCreateRequest } from '../services/api/tournaments';

export const TournamentEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const tournamentId = Number(id);
  const navigate = useNavigate();
  const { currentPlayer } = useAuth();
  const updateMutation = useUpdateTournament();

  const { data: tournamentList, isLoading } = useAllTournaments();
  const tournament = tournamentList?.tournaments.find(t => t.id === tournamentId);

  if (isLoading) return <div className="loading">Loading...</div>;

  if (!tournament) {
    return (
      <div>
        <p>Tournament not found.</p>
        <Link to="/tournaments">← Back to Tournaments</Link>
      </div>
    );
  }

  if (!currentPlayer || currentPlayer.id !== tournament.creator_id) {
    return (
      <div>
        <p>You are not authorized to edit this tournament.</p>
        <Link to={`/tournaments/${tournamentId}`}>← Back to Tournament</Link>
      </div>
    );
  }

  // Convert ISO date to datetime-local format (YYYY-MM-DDTHH:MM)
  const localStartTime = tournament.start_time
    ? new Date(tournament.start_time).toISOString().slice(0, 16)
    : '';

  const initialValues: Partial<TournamentCreateRequest> = {
    name: tournament.name,
    rank_tier: tournament.rank_tier,
    region: tournament.region,
    capacity: tournament.capacity,
    format: tournament.format,
    start_time: localStartTime,
    is_team_tournament: tournament.is_team_tournament === 1,
    team_size: tournament.team_size,
  };

  const handleUpdate = async (request: TournamentCreateRequest) => {
    try {
      await updateMutation.mutateAsync({
        id: tournamentId,
        data: {
          name: request.name,
          rank_tier: request.rank_tier,
          region: request.region,
          capacity: request.capacity,
          format: request.format,
          start_time: request.start_time,
        },
      });
      alert('Tournament updated successfully!');
      navigate(`/tournaments/${tournamentId}`);
    } catch (error: any) {
      const detail = error?.response?.data?.detail;
      const errorMessage = typeof detail === 'string' ? detail : 'Failed to update tournament';
      alert(`Error: ${errorMessage}`);
    }
  };

  return (
    <div className="tournament-create-page">
      <Link to={`/tournaments/${tournamentId}`} style={{ color: '#666', textDecoration: 'none', fontSize: 14 }}>
        ← Back to Tournament
      </Link>
      <h1 style={{ marginTop: 16 }}>Edit Tournament</h1>
      <TournamentForm
        onCreateTournament={handleUpdate}
        isLoading={updateMutation.isPending}
        initialValues={initialValues}
        submitLabel="Save Changes"
      />
    </div>
  );
};
