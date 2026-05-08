import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAllTournaments } from '../hooks/useTournaments';
import { useTournamentMatches, useRecordResult } from '../hooks/useMatches';
import { BracketView } from '../components/BracketView';
import { tournamentsApi } from '../services/api/tournaments';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';

export const TournamentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const tournamentId = Number(id);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { currentPlayer } = useAuth();
  const [generating, setGenerating] = useState(false);
  const [pendingMatchId, setPendingMatchId] = useState<number | null>(null);

  const { data: tournamentList, isLoading: loadingTournament } = useAllTournaments();
  const { data: matches, isLoading: loadingMatches } = useTournamentMatches(tournamentId);
  const recordResult = useRecordResult(tournamentId);

  const tournament = tournamentList?.tournaments.find(t => t.id === tournamentId);

  if (loadingTournament || loadingMatches) {
    return <div className="loading">Loading...</div>;
  }

  if (!tournament) {
    return (
      <div>
        <p>Tournament not found.</p>
        <Link to="/tournaments">← Back to Tournaments</Link>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Link to="/tournaments" style={{ color: '#666', textDecoration: 'none', fontSize: 14 }}>
        ← Back to Tournaments
      </Link>

      <h1 style={{ marginTop: 16 }}>{tournament.name}</h1>

      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginBottom: 32 }}>
        <Stat label="Status" value={tournament.status} />
        <Stat label="Rank" value={tournament.rank_tier} />
        <Stat label="Region" value={tournament.region} />
        <Stat label="Format" value={tournament.format} />
        <Stat label="Players" value={`${tournament.registered_count} / ${tournament.capacity}`} />
        <Stat label="Start" value={new Date(tournament.start_time).toLocaleString()} />
        <Stat label="Creator" value={tournament.creator_username ?? '—'} />
      </div>

      {currentPlayer && currentPlayer.id === tournament.creator_id && (
        <div style={{ marginBottom: 24 }}>
          <button
            onClick={() => navigate(`/tournaments/${tournamentId}/edit`)}
            style={{ padding: '8px 18px', cursor: 'pointer', background: '#4a6cf7', color: '#fff', border: 'none', borderRadius: 6 }}
          >
            Edit Tournament
          </button>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Tournament Bracket</h2>
        {currentPlayer?.id === tournament.creator_id &&
          tournament.status !== 'IN_PROGRESS' &&
          tournament.status !== 'COMPLETED' && (
          <button
            onClick={async () => {
              setGenerating(true);
              try {
                await tournamentsApi.generateBracket(tournamentId);
                queryClient.invalidateQueries({ queryKey: ['matches', tournamentId] });
                queryClient.invalidateQueries({ queryKey: ['tournaments'] });
              } finally {
                setGenerating(false);
              }
            }}
            disabled={generating}
            style={{ padding: '6px 14px', cursor: 'pointer' }}
          >
            {generating ? 'Generating...' : 'Generate Bracket'}
          </button>
        )}
      </div>
      <BracketView
        matches={matches ?? []}
        isCreator={currentPlayer?.id === tournament.creator_id}
        onRecordResult={(matchId, winnerId, loserId) => {
          setPendingMatchId(matchId);
          recordResult.mutate(
            { matchId, winnerId, loserId },
            { onSettled: () => setPendingMatchId(null) }
          );
        }}
        pendingMatchId={pendingMatchId}
      />
    </div>
  );
};

const Stat: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div style={{
    background: '#f5f5f5',
    borderRadius: 8,
    padding: '10px 16px',
    minWidth: 100,
  }}>
    <div style={{ fontSize: 11, color: '#888', textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</div>
    <div style={{ fontWeight: 600, marginTop: 4 }}>{value}</div>
  </div>
);
