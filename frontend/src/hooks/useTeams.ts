// Feature: F002
// Scenario: SC003, SC004
// Team Hooks

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { teamsApi, TeamCreateRequest, TeamInviteRequest } from '../services/api/teams';

/**
 * Feature: F002
 * Scenario: SC003
 * Hook to create a team
 */
export const useCreateTeam = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ownerId, data }: { ownerId: number; data: TeamCreateRequest }) =>
      teamsApi.createTeam(ownerId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });
};

/**
 * Feature: F002
 * Scenario: SC003
 * Hook to create team invite
 */
export const useCreateInvite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ ownerId, data }: { ownerId: number; data: TeamInviteRequest }) =>
      teamsApi.createInvite(ownerId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invites'] });
    },
  });
};

/**
 * Feature: F002
 * Scenario: SC003
 * Hook to accept team invite
 */
export const useAcceptInvite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ token, playerId }: { token: string; playerId: number }) =>
      teamsApi.acceptInvite(token, playerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
    },
  });
};

/**
 * Feature: F002
 * Scenario: SC003
 * Hook to get team roster
 */
export const useTeamRoster = (teamId: number) => {
  return useQuery({
    queryKey: ['teams', teamId, 'roster'],
    queryFn: () => teamsApi.getTeamRoster(teamId),
    enabled: !!teamId,
  });
};

/**
 * Feature: F002
 * Scenario: SC004
 * Hook to register team for tournament
 */
export const useRegisterTeamForTournament = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      teamId,
      tournamentId,
      ownerId,
    }: {
      teamId: number;
      tournamentId: number;
      ownerId: number;
    }) => teamsApi.registerTeamForTournament(teamId, tournamentId, ownerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
      queryClient.invalidateQueries({ queryKey: ['tournaments'] });
    },
  });
};

/**
 * Feature: F002
 * Hook to revoke invite
 */
export const useRevokeInvite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ token, ownerId }: { token: string; ownerId: number }) =>
      teamsApi.revokeInvite(token, ownerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invites'] });
    },
  });
};
