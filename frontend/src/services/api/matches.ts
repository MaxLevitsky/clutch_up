import apiClient from './client';

export interface MatchResponse {
  id: number;
  tournament_id: number;
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  round_number: number;
  player1_id: number | null;
  player2_id: number | null;
  winner_id: number | null;
  loser_id: number | null;
  player1_username: string | null;
  player2_username: string | null;
  winner_username: string | null;
  scheduled_time: string;
  completed_at: string | null;
  created_at: string;
}

export const matchesApi = {
  getTournamentMatches: async (tournamentId: number): Promise<MatchResponse[]> => {
    const response = await apiClient.get<MatchResponse[]>(`/matches/tournament/${tournamentId}`);
    return response.data;
  },

  recordResult: async (matchId: number, winnerId: number, loserId: number): Promise<MatchResponse> => {
    const response = await apiClient.post<MatchResponse>(`/matches/${matchId}/result`, {
      winner_id: winnerId,
      loser_id: loserId,
    });
    return response.data;
  },
};
