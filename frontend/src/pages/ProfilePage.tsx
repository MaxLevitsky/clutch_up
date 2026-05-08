// Feature: F003
// Scenario: SC005
// Requirement: FR-12

import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { getPlayerProfile, getAllBadges } from '../services/api/progression';
import ProgressionBar from '../components/ProgressionBar';
import BadgeDisplay from '../components/BadgeDisplay';

const RANK_COLORS: Record<string, string> = {
  BEGINNER: '#4caf50',
  INTERMEDIATE: '#2196f3',
  ADVANCED: '#ff9800',
  EXPERT: '#9c27b0',
};

export default function ProfilePage() {
  const { currentPlayer } = useAuth();
  const playerId = currentPlayer!.id;

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile', playerId],
    queryFn: () => getPlayerProfile(playerId),
  });

  const { data: allBadges } = useQuery({
    queryKey: ['badges'],
    queryFn: getAllBadges,
  });

  if (profileLoading) return <div style={{ padding: 32 }}>Loading profile...</div>;
  if (!profile) return <div style={{ padding: 32 }}>Profile not found.</div>;

  const rankColor = RANK_COLORS[profile.rank] ?? '#888';

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', padding: '0 16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24 }}>
        <div style={{
          width: 72, height: 72, borderRadius: '50%',
          background: rankColor, display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 28, color: '#fff', fontWeight: 700,
        }}>
          {profile.username[0].toUpperCase()}
        </div>
        <div>
          <h2 style={{ margin: 0 }}>{profile.username}</h2>
          <span style={{
            display: 'inline-block', marginTop: 4, padding: '2px 10px',
            borderRadius: 12, background: rankColor, color: '#fff', fontSize: 13,
          }}>
            {profile.rank}
          </span>
          <span style={{ marginLeft: 8, color: '#555', fontSize: 14 }}>{profile.region}</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 24, marginBottom: 24, flexWrap: 'wrap' }}>
        <StatCard label="Tournaments Played" value={profile.tournaments_played} />
        <StatCard label="Matches Won" value={profile.matches_won} />
        <StatCard label="Level" value={profile.level} />
        <StatCard label="Total Points" value={profile.points} />
      </div>

      <ProgressionBar
        level={profile.level}
        points={profile.points}
        pointsToNextLevel={profile.points_to_next_level}
      />

      <BadgeDisplay badges={profile.badges} allBadges={allBadges} />
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div style={{
      background: '#f5f5f5', borderRadius: 12, padding: '12px 20px',
      textAlign: 'center', minWidth: 120,
    }}>
      <div style={{ fontSize: 28, fontWeight: 700 }}>{value}</div>
      <div style={{ fontSize: 13, color: '#555', marginTop: 4 }}>{label}</div>
    </div>
  );
}
