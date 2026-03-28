// Feature: F002
// Scenario: SC003, SC004
// Team API Client

import apiClient from './client';

export interface Team {
  id: number;
  name: string;
  badge?: string;
  owner_id: number;
  created_at: string;
}

export interface TeamCreateRequest {
  name: string;
  badge?: string;
}

export interface TeamInviteRequest {
  team_id: number;
}

export const teamsApi = {
  /**
   * Feature: F002
   * Scenario: SC003
   * Requirement: FR-6
   * Create a new team
   */
  createTeam: async (ownerId: number, data: TeamCreateRequest): Promise<any> => {
    const response = await apiClient.post(`/teams/?owner_id=${ownerId}`, data);
    return response.data;
  },

  /**
   * Feature: F002
   * Scenario: SC003
   * Requirement: FR-7
   * Create team invite
   */
  createInvite: async (ownerId: number, data: TeamInviteRequest): Promise<any> => {
    const response = await apiClient.post(`/teams/invites?owner_id=${ownerId}`, data);
    return response.data;
  },

  /**
   * Feature: F002
   * Scenario: SC003
   * Requirement: FR-7
   * Accept team invite
   */
  acceptInvite: async (token: string, playerId: number): Promise<any> => {
    const response = await apiClient.post(
      `/teams/invites/${token}/accept?player_id=${playerId}`
    );
    return response.data;
  },

  /**
   * Feature: F002
   * Scenario: SC003
   * Requirement: FR-8
   * Get team roster
   */
  getTeamRoster: async (teamId: number): Promise<any> => {
    const response = await apiClient.get(`/teams/${teamId}/roster`);
    return response.data;
  },

  /**
   * Feature: F002
   * Scenario: SC004
   * Requirement: FR-9, FR-10
   * Register team for tournament
   */
  registerTeamForTournament: async (
    teamId: number,
    tournamentId: number,
    ownerId: number
  ): Promise<any> => {
    const response = await apiClient.post(
      `/teams/${teamId}/register-tournament/${tournamentId}?owner_id=${ownerId}`
    );
    return response.data;
  },

  /**
   * Feature: F002
   * Requirement: NFR-7
   * Revoke team invite
   */
  revokeInvite: async (token: string, ownerId: number): Promise<any> => {
    const response = await apiClient.delete(
      `/teams/invites/${token}/revoke?owner_id=${ownerId}`
    );
    return response.data;
  },
};
