// Feature: F003

import { BadgeResponse } from '../services/api/progression';

interface Props {
  badges: BadgeResponse[];
  allBadges?: BadgeResponse[];
}

const BADGE_ICONS: Record<string, string> = {
  'First Steps': '🎯',
  'Team Player': '🤝',
  'Match Victor': '⚔️',
  'Champion': '🏆',
  'Veteran': '⭐',
};

export default function BadgeDisplay({ badges, allBadges }: Props) {
  const earnedIds = new Set(badges.map(b => b.id));
  const displayBadges = allBadges ?? badges;

  return (
    <div>
      <h3>Badges</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
        {displayBadges.map(badge => {
          const earned = earnedIds.has(badge.id);
          return (
            <div
              key={badge.id}
              title={badge.description ?? badge.name}
              style={{
                padding: '12px 16px',
                borderRadius: 12,
                background: earned ? '#e8f5e9' : '#f5f5f5',
                border: earned ? '2px solid #4caf50' : '2px solid #e0e0e0',
                opacity: earned ? 1 : 0.45,
                textAlign: 'center',
                minWidth: 90,
              }}
            >
              <div style={{ fontSize: 28 }}>{BADGE_ICONS[badge.name] ?? '🎖️'}</div>
              <div style={{ fontSize: 12, fontWeight: 600, marginTop: 4 }}>{badge.name}</div>
            </div>
          );
        })}
        {displayBadges.length === 0 && <p style={{ color: '#888' }}>No badges yet — keep playing!</p>}
      </div>
    </div>
  );
}
