// Feature: F001, F002, F003
// Player API Client

import apiClient from './client';

export interface Player {
  id: number;
  username: string;
  email: string;
  rank: string;
  region: string;
  progression_level: number;
  account_status: string;
  created_at: string;
}

export interface PlayerCreateRequest {
  username: string;
  email: string;
  region: string;
}

export const playersApi = {
  /**
   * Create a new player
   */
  createPlayer: async (data: PlayerCreateRequest): Promise<Player> => {
    const response = await apiClient.post<Player>('/players/', data);
    return response.data;
  },

  /**
   * Get player by ID
   */
  getPlayer: async (playerId: number): Promise<Player> => {
    const response = await apiClient.get<Player>(`/players/${playerId}`);
    return response.data;
  },
};
