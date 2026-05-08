import React from 'react';
import { MatchResponse } from '../services/api/matches';

interface BracketViewProps {
  matches: MatchResponse[];
  isCreator?: boolean;
  onRecordResult?: (matchId: number, winnerId: number, loserId: number) => void;
  pendingMatchId?: number | null;
}

function roundLabel(round: number, maxRound: number): string {
  if (round === maxRound && maxRound > 1) return `Final (Round ${round})`;
  if (round === maxRound - 1 && maxRound > 2) return `Semifinal (Round ${round})`;
  return `Round ${round}`;
}

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    SCHEDULED: '#888',
    IN_PROGRESS: '#e8a000',
    COMPLETED: '#2e7d32',
    CANCELLED: '#c62828',
  };
  return (
    <span style={{
      fontSize: 11,
      padding: '2px 7px',
      borderRadius: 10,
      background: colors[status] || '#888',
      color: '#fff',
      marginLeft: 8,
    }}>
      {status}
    </span>
  );
}

export const BracketView: React.FC<BracketViewProps> = ({ matches, isCreator, onRecordResult, pendingMatchId }) => {
  if (!matches.length) {
    return <p style={{ color: '#888' }}>No matches yet for this tournament.</p>;
  }

  const rounds = [...new Set(matches.map(m => m.round_number))].sort((a, b) => a - b);
  const maxRound = Math.max(...rounds);

  const canRecord = (match: MatchResponse) =>
    isCreator &&
    match.status === 'SCHEDULED' &&
    match.player1_id !== null &&
    match.player2_id !== null &&
    onRecordResult !== undefined;

  return (
    <div style={{ display: 'flex', gap: 24, overflowX: 'auto', paddingBottom: 12 }}>
      {rounds.map(round => (
        <div key={round} style={{ minWidth: 220 }}>
          <h3 style={{ fontSize: 14, textTransform: 'uppercase', letterSpacing: 1, color: '#555', marginBottom: 12 }}>
            {roundLabel(round, maxRound)}
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {matches.filter(m => m.round_number === round).map(match => (
              <div key={match.id} style={{
                border: '1px solid #ddd',
                borderRadius: 8,
                overflow: 'hidden',
                background: '#fafafa',
              }}>
                <PlayerRow
                  username={match.player1_username}
                  isWinner={match.winner_id === match.player1_id && match.winner_id !== null}
                  status={match.status}
                />
                <div style={{ height: 1, background: '#ddd' }} />
                <PlayerRow
                  username={match.player2_username}
                  isWinner={match.winner_id === match.player2_id && match.winner_id !== null}
                  status={match.status}
                />
                <div style={{ padding: '4px 10px', background: '#f0f0f0', fontSize: 11, color: '#888', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Match #{match.id}</span>
                  {statusBadge(match.status)}
                </div>
                {canRecord(match) && (
                  <div style={{ padding: '8px 10px', background: '#fff8e1', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    <button
                      disabled={pendingMatchId === match.id}
                      onClick={() => onRecordResult!(match.id, match.player1_id!, match.player2_id!)}
                      style={{ flex: 1, padding: '4px 8px', fontSize: 12, cursor: 'pointer', background: '#4a6cf7', color: '#fff', border: 'none', borderRadius: 4 }}
                    >
                      {pendingMatchId === match.id ? '...' : `${match.player1_username} wins`}
                    </button>
                    <button
                      disabled={pendingMatchId === match.id}
                      onClick={() => onRecordResult!(match.id, match.player2_id!, match.player1_id!)}
                      style={{ flex: 1, padding: '4px 8px', fontSize: 12, cursor: 'pointer', background: '#4a6cf7', color: '#fff', border: 'none', borderRadius: 4 }}
                    >
                      {pendingMatchId === match.id ? '...' : `${match.player2_username} wins`}
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

interface PlayerRowProps {
  username: string | null;
  isWinner: boolean;
  status: string;
}

const PlayerRow: React.FC<PlayerRowProps> = ({ username, isWinner, status }) => (
  <div style={{
    padding: '8px 12px',
    fontWeight: isWinner ? 700 : 400,
    color: isWinner ? '#2e7d32' : status === 'COMPLETED' ? '#999' : '#222',
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    background: isWinner ? '#f1f8e9' : 'transparent',
  }}>
    {isWinner && <span>🏆</span>}
    {username ?? <span style={{ color: '#bbb', fontStyle: 'italic' }}>TBD</span>}
  </div>
);
