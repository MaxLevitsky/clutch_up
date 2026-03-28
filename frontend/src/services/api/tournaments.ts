// Feature: F001
// Scenario: SC001, SC002
// Tournament API Client

import apiClient from './client';

export interface Tournament {
  id: number;
  name: string;
  rank_tier: string;
  region: string;
  capacity: number;
  registered_count: number;
  status: string;
  start_time: string;
  format: string;
  is_team_tournament: number;
  team_size?: number;
}

export interface TournamentListResponse {
  tournaments: Tournament[];
  total: number;
}

export interface RegistrationRequest {
  tournament_id: number;
  team_id?: number;
}

export interface RegistrationResponse {
  status: string;
  message: string;
  tournament_id: number;
  player_id: number;
  registered_at?: string;
  eligibility?: any;
}

export const tournamentsApi = {
  /**
   * Feature: F001
   * Scenario: SC001
   * Requirement: FR-1
   * Get eligible tournaments for a player
   */
  getEligibleTournaments: async (playerId: number): Promise<TournamentListResponse> => {
    const response = await apiClient.get<TournamentListResponse>(
      `/tournaments/eligible/${playerId}`
    );
    return response.data;
  },

  /**
   * Get all tournaments
   */
  getAllTournaments: async (): Promise<TournamentListResponse> => {
    const response = await apiClient.get<TournamentListResponse>('/tournaments/');
    return response.data;
  },

  /**
   * Feature: F001
   * Scenario: SC001, SC002
   * Requirement: FR-2, FR-3
   * Register player for tournament
   */
  registerForTournament: async (
    playerId: number,
    request: RegistrationRequest
  ): Promise<RegistrationResponse> => {
    const response = await apiClient.post<RegistrationResponse>(
      `/tournaments/register?player_id=${playerId}`,
      request
    );
    return response.data;
  },

  /**
   * Feature: F001
   * Scenario: SC002
   * Requirement: FR-4, FR-5
   * Validate tournament eligibility
   */
  validateEligibility: async (
    playerId: number,
    tournamentId: number
  ): Promise<any> => {
    const response = await apiClient.get(
      `/tournaments/validate-eligibility/${playerId}/${tournamentId}`
    );
    return response.data;
  },
};
