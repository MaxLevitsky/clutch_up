import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { matchesApi } from '../services/api/matches';

export const useTournamentMatches = (tournamentId: number) => {
  return useQuery({
    queryKey: ['matches', tournamentId],
    queryFn: () => matchesApi.getTournamentMatches(tournamentId),
    enabled: !!tournamentId,
  });
};

export const useRecordResult = (tournamentId: number) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ matchId, winnerId, loserId }: { matchId: number; winnerId: number; loserId: number }) =>
      matchesApi.recordResult(matchId, winnerId, loserId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches', tournamentId] });
      queryClient.invalidateQueries({ queryKey: ['tournaments'] });
    },
  });
};
