// Feature: F003

interface Props {
  level: number;
  points: number;
  pointsToNextLevel: number;
}

export default function ProgressionBar({ level, points, pointsToNextLevel }: Props) {
  const pointsInLevel = 100 - pointsToNextLevel;
  const pct = level >= 50 ? 100 : Math.round((pointsInLevel / 100) * 100);

  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span><strong>Level {level}</strong> — {points} total points</span>
        {level < 50 && <span>{pointsToNextLevel} pts to next level</span>}
      </div>
      <div style={{ background: '#e0e0e0', borderRadius: 8, height: 16, overflow: 'hidden' }}>
        <div
          style={{
            width: `${pct}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #4caf50, #81c784)',
            transition: 'width 0.4s ease',
          }}
        />
      </div>
    </div>
  );
}
