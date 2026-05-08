// Feature: Authentication

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { TokenResponse, registerPlayer, loginPlayer, RegisterRequest } from '../services/api/auth';

interface CurrentPlayer {
  id: number;
  username: string;
  rank: string;
  token: string;
}

interface AuthContextValue {
  currentPlayer: CurrentPlayer | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = 'clutchup_token';
const PLAYER_KEY = 'clutchup_player';

function loadFromStorage(): CurrentPlayer | null {
  try {
    const raw = localStorage.getItem(PLAYER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentPlayer, setCurrentPlayer] = useState<CurrentPlayer | null>(loadFromStorage);

  const persist = useCallback((resp: TokenResponse) => {
    const player: CurrentPlayer = {
      id: resp.player_id,
      username: resp.username,
      rank: resp.rank,
      token: resp.access_token,
    };
    localStorage.setItem(TOKEN_KEY, resp.access_token);
    localStorage.setItem(PLAYER_KEY, JSON.stringify(player));
    setCurrentPlayer(player);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const resp = await loginPlayer(username, password);
    persist(resp);
  }, [persist]);

  const register = useCallback(async (data: RegisterRequest) => {
    const resp = await registerPlayer(data);
    persist(resp);
  }, [persist]);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(PLAYER_KEY);
    setCurrentPlayer(null);
  }, []);

  return (
    <AuthContext.Provider value={{ currentPlayer, login, register, logout, isAuthenticated: !!currentPlayer }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
