// Feature: F004
// Scenario: SC007
// Tournament Creation Page

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TournamentForm } from '../components/TournamentForm';
import { useCreateTournament } from '../hooks/useTournaments';
import { TournamentCreateRequest } from '../services/api/tournaments';

/**
 * Feature: F004
 * Scenario: SC007
 * Requirements: FR-13, FR-14, FR-15, FR-16
 * Tournament creation page for organizers
 */
export const TournamentCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const createMutation = useCreateTournament();

  const handleCreateTournament = async (request: TournamentCreateRequest) => {
    try {
      const tournament = await createMutation.mutateAsync(request);
      alert(`Tournament "${tournament.name}" created successfully!`);
      // NFR-14: Navigate to tournaments list to see newly created tournament
      navigate('/tournaments');
    } catch (error: any) {
      // NFR-13: Display validation error messages
      const detail = error?.response?.data?.detail;
      const errorMessage = Array.isArray(detail)
        ? detail.map((e: any) => e.msg ?? JSON.stringify(e)).join('; ')
        : (typeof detail === 'string' ? detail : 'Failed to create tournament');
      alert(`Error: ${errorMessage}`);
      console.error(error);
    }
  };

  return (
    <div className="tournament-create-page">
      <h1>Create New Tournament</h1>
      <TournamentForm
        onCreateTournament={handleCreateTournament}
        isLoading={createMutation.isPending}
      />
    </div>
  );
};
