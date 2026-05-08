// Feature: Authentication

import apiClient from './client';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  player_id: number;
  username: string;
  rank: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  region: string;
}

export const registerPlayer = async (data: RegisterRequest): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/register', data);
  return response.data;
};

export const loginPlayer = async (username: string, password: string): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>('/auth/login', { username, password });
  return response.data;
};
