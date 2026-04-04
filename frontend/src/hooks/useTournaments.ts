// Feature: F001, F004
// Scenario: SC001, SC002, SC007
// Tournament Hooks

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tournamentsApi, RegistrationRequest, TournamentCreateRequest } from '../services/api/tournaments';

/**
 * Feature: F001
 * Scenario: SC001
 * Hook to fetch eligible tournaments for a player
 */
export const useEligibleTournaments = (playerId: number) => {
  return useQuery({
    queryKey: ['tournaments', 'eligible', playerId],
    queryFn: () => tournamentsApi.getEligibleTournaments(playerId),
    enabled: !!playerId,
  });
};

/**
 * Hook to fetch all tournaments
 */
export const useAllTournaments = () => {
  return useQuery({
    queryKey: ['tournaments', 'all'],
    queryFn: () => tournamentsApi.getAllTournaments(),
  });
};

/**
 * Feature: F001
 * Scenario: SC001, SC002
 * Hook to register for a tournament
 */
export const useRegisterTournament = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      playerId,
      request,
    }: {
      playerId: number;
      request: RegistrationRequest;
    }) => tournamentsApi.registerForTournament(playerId, request),
    onSuccess: () => {
      // Invalidate tournaments query to refresh data
      queryClient.invalidateQueries({ queryKey: ['tournaments'] });
    },
  });
};

/**
 * Feature: F001
 * Scenario: SC002
 * Hook to validate tournament eligibility
 */
export const useValidateEligibility = (playerId: number, tournamentId: number) => {
  return useQuery({
    queryKey: ['tournaments', 'eligibility', playerId, tournamentId],
    queryFn: () => tournamentsApi.validateEligibility(playerId, tournamentId),
    enabled: !!playerId && !!tournamentId,
  });
};

/**
 * Feature: F004
 * Scenario: SC007
 * Requirements: FR-13, FR-14, FR-15, FR-16
 * Hook to create a tournament
 */
export const useCreateTournament = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: TournamentCreateRequest) =>
      tournamentsApi.createTournament(request),
    onSuccess: () => {
      // NFR-14: Invalidate tournaments query to show newly created tournament
      queryClient.invalidateQueries({ queryKey: ['tournaments'] });
    },
  });
};
