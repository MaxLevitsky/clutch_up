// Feature: F003

import apiClient from './client';

export interface BadgeResponse {
  id: number;
  name: string;
  description: string | null;
  icon_url: string | null;
}

export interface ProgressionResponse {
  player_id: number;
  points: number;
  level: number;
  badges: BadgeResponse[];
  tournaments_played: number;
  matches_won: number;
  points_to_next_level: number;
}

export interface PlayerProfileResponse {
  id: number;
  username: string;
  email: string;
  rank: string;
  region: string;
  account_status: string;
  created_at: string;
  points: number;
  level: number;
  badges: BadgeResponse[];
  tournaments_played: number;
  matches_won: number;
  points_to_next_level: number;
}

export const getPlayerProfile = async (playerId: number): Promise<PlayerProfileResponse> => {
  const response = await apiClient.get<PlayerProfileResponse>(`/players/${playerId}/profile`);
  return response.data;
};

export const getAllBadges = async (): Promise<BadgeResponse[]> => {
  const response = await apiClient.get<BadgeResponse[]>('/progression/badges/');
  return response.data;
};
