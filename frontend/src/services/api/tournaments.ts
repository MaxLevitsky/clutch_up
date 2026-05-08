// Feature: F001, F004
// Scenario: SC001, SC002, SC007
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
  creator_id?: number;
  creator_username?: string;
}

export interface TournamentUpdatePayload {
  name?: string;
  rank_tier?: string;
  region?: string;
  capacity?: number;
  format?: string;
  start_time?: string;
}

export interface TournamentCreateRequest {
  name: string;
  rank_tier: string;
  region: string;
  capacity: number;
  format: string;
  start_time: string;
  is_team_tournament: boolean;
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

  /**
   * Feature: F004
   * Scenario: SC007
   * Requirements: FR-13, FR-14, FR-15, FR-16
   * Create a new tournament
   */
  createTournament: async (request: TournamentCreateRequest): Promise<Tournament> => {
    const response = await apiClient.post<Tournament>('/tournaments/', request);
    return response.data;
  },

  generateBracket: async (tournamentId: number): Promise<void> => {
    await apiClient.post(`/tournaments/${tournamentId}/generate-bracket`);
  },

  updateTournament: async (tournamentId: number, data: TournamentUpdatePayload): Promise<Tournament> => {
    const response = await apiClient.put<Tournament>(`/tournaments/${tournamentId}`, data);
    return response.data;
  },
};
