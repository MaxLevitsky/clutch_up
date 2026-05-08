// Feature: F004
// Scenario: SC007
// Tournament Creation Form Component

import React, { useState } from 'react';
import { TournamentCreateRequest } from '../services/api/tournaments';

interface TournamentFormProps {
  onCreateTournament: (request: TournamentCreateRequest) => void;
  isLoading?: boolean;
  initialValues?: Partial<TournamentCreateRequest>;
  submitLabel?: string;
}

/**
 * Feature: F004
 * Scenario: SC007
 * Requirements: FR-13, FR-14, FR-15, FR-16
 * Tournament creation form with validation
 */
export const TournamentForm: React.FC<TournamentFormProps> = ({
  onCreateTournament,
  isLoading,
  initialValues,
  submitLabel,
}) => {
  const [name, setName] = useState(initialValues?.name ?? '');
  const [rankTier, setRankTier] = useState(initialValues?.rank_tier ?? 'BEGINNER');
  const [region, setRegion] = useState(initialValues?.region ?? 'NA');
  const [capacity, setCapacity] = useState(initialValues?.capacity ?? 16);
  const [format, setFormat] = useState(initialValues?.format ?? 'Single Elimination');
  const [startTime, setStartTime] = useState(initialValues?.start_time ?? '');
  const [isTeamTournament, setIsTeamTournament] = useState(initialValues?.is_team_tournament ?? false);
  const [teamSize, setTeamSize] = useState<number | undefined>(initialValues?.team_size);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (capacity < 1 || capacity > 64) {
      alert('Capacity must be between 1 and 64');
      return;
    }

    // FR-14: Validate start time is in future
    const startDate = new Date(startTime);
    if (startDate <= new Date()) {
      alert('Start time must be in the future');
      return;
    }

    // FR-16: Validate team_size consistency
    if (isTeamTournament && !teamSize) {
      alert('Team tournaments must specify team size');
      return;
    }

    if (!isTeamTournament && teamSize) {
      alert('Solo tournaments must not specify team size');
      return;
    }

    // FR-16: Validate team_size range (2-5)
    if (teamSize && (teamSize < 2 || teamSize > 5)) {
      alert('Team size must be between 2 and 5');
      return;
    }

    onCreateTournament({
      name,
      rank_tier: rankTier,
      region,
      capacity,
      format,
      start_time: startTime,
      is_team_tournament: isTeamTournament,
      team_size: isTeamTournament ? teamSize : undefined,
    });
  };

  return (
    <div className="tournament-form">
      <h2>{submitLabel ? submitLabel.replace(/\b\w/, c => c.toUpperCase()) : 'Create Tournament'}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Tournament Name *</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter tournament name"
            required
            disabled={isLoading}
            maxLength={200}
          />
        </div>

        <div className="form-group">
          <label htmlFor="rankTier">Rank Tier *</label>
          <select
            id="rankTier"
            value={rankTier}
            onChange={(e) => setRankTier(e.target.value)}
            required
            disabled={isLoading}
          >
            <option value="BEGINNER">Beginner</option>
            <option value="INTERMEDIATE">Intermediate</option>
            <option value="ADVANCED">Advanced</option>
            <option value="EXPERT">Expert</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="region">Region *</label>
          <select
            id="region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            required
            disabled={isLoading}
          >
            <option value="NA">North America</option>
            <option value="EU">Europe</option>
            <option value="ASIA">Asia</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="capacity">Capacity * (1-64)</label>
          <input
            type="number"
            id="capacity"
            value={capacity}
            onChange={(e) => setCapacity(Number(e.target.value))}
            min={1}
            max={64}
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="format">Format *</label>
          <input
            type="text"
            id="format"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            placeholder="e.g., Single Elimination, Double Elimination"
            required
            disabled={isLoading}
            maxLength={100}
          />
        </div>

        <div className="form-group">
          <label htmlFor="startTime">Start Time *</label>
          <input
            type="datetime-local"
            id="startTime"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={isTeamTournament}
              onChange={(e) => {
                setIsTeamTournament(e.target.checked);
                if (!e.target.checked) {
                  setTeamSize(undefined);
                }
              }}
              disabled={isLoading}
            />
            Team Tournament
          </label>
        </div>

        {isTeamTournament && (
          <div className="form-group">
            <label htmlFor="teamSize">Team Size * (2-5)</label>
            <input
              type="number"
              id="teamSize"
              value={teamSize || ''}
              onChange={(e) => setTeamSize(Number(e.target.value) || undefined)}
              min={2}
              max={5}
              required={isTeamTournament}
              disabled={isLoading}
            />
          </div>
        )}

        <button type="submit" disabled={isLoading || !name.trim()}>
          {isLoading ? 'Saving...' : (submitLabel ?? 'Create Tournament')}
        </button>
      </form>
    </div>
  );
};
