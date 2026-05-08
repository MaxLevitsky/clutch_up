// Test Case: TC-FR-001-INT, TC-FR-013-INT, Requirement: FR-1, FR-13
// Feature: F001, F004
// Scenario: SC001, SC007
// Frontend Unit Tests for useTournaments Hook

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAllTournaments, useEligibleTournaments, useCreateTournament, useRegisterTournament, useUpdateTournament } from './useTournaments';
import { tournamentsApi } from '../services/api/tournaments';
import React from 'react';

// Mock the tournaments API
vi.mock('../services/api/tournaments', () => ({
  tournamentsApi: {
    getAllTournaments: vi.fn(),
    getEligibleTournaments: vi.fn(),
    createTournament: vi.fn(),
    registerForTournament: vi.fn(),
    updateTournament: vi.fn(),
  },
}));

describe('useTournaments Hooks', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);

  // TC-FR-001-INT: Test useAllTournaments hook
  describe('useAllTournaments', () => {
    it('should fetch all tournaments successfully', async () => {
      const mockTournaments = [
        {
          id: 1,
          name: 'Beginner Championship',
          rank_tier: 'BEGINNER',
          region: 'NA',
          capacity: 16,
          registered_count: 5,
          status: 'UPCOMING',
        },
        {
          id: 2,
          name: 'EU Masters',
          rank_tier: 'INTERMEDIATE',
          region: 'EU',
          capacity: 32,
          registered_count: 12,
          status: 'REGISTRATION_OPEN',
        },
      ];

      vi.mocked(tournamentsApi.getAllTournaments).mockResolvedValue(mockTournaments);

      const { result } = renderHook(() => useAllTournaments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockTournaments);
      expect(tournamentsApi.getAllTournaments).toHaveBeenCalledTimes(1);
    });

    it('should handle API error gracefully', async () => {
      vi.mocked(tournamentsApi.getAllTournaments).mockRejectedValue(
        new Error('Network error')
      );

      const { result } = renderHook(() => useAllTournaments(), { wrapper });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // TC-FR-001-INT: Test useEligibleTournaments hook
  describe('useEligibleTournaments', () => {
    it('should fetch eligible tournaments for player', async () => {
      const playerId = 1;
      const mockEligibleTournaments = [
        {
          id: 1,
          name: 'Beginner Only',
          rank_tier: 'BEGINNER',
          region: 'NA',
          capacity: 16,
          registered_count: 5,
          status: 'REGISTRATION_OPEN',
        },
      ];

      vi.mocked(tournamentsApi.getEligibleTournaments).mockResolvedValue(
        mockEligibleTournaments
      );

      const { result } = renderHook(() => useEligibleTournaments(playerId), { wrapper });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockEligibleTournaments);
      expect(tournamentsApi.getEligibleTournaments).toHaveBeenCalledWith(playerId);
    });

    it('should not fetch when playerId is 0', () => {
      const { result } = renderHook(() => useEligibleTournaments(0), { wrapper });

      expect(result.current.isPending).toBe(true);
      expect(result.current.fetchStatus).toBe('idle');
      expect(tournamentsApi.getEligibleTournaments).not.toHaveBeenCalled();
    });
  });

  // TC-FR-013-INT: Test useCreateTournament hook
  describe('useCreateTournament', () => {
    it('should create tournament successfully', async () => {
      const mockRequest = {
        name: 'New Tournament',
        rank_tier: 'BEGINNER',
        region: 'NA',
        capacity: 16,
        format: 'Single Elimination',
        start_time: '2026-05-01T10:00:00',
        is_team_tournament: false,
        team_size: undefined,
      };

      const mockResponse = {
        status: 'success',
        message: "Tournament 'New Tournament' created successfully",
        tournament: {
          id: 3,
          ...mockRequest,
          status: 'UPCOMING',
          registered_count: 0,
        },
      };

      vi.mocked(tournamentsApi.createTournament).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useCreateTournament(), { wrapper });

      result.current.mutate(mockRequest);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
      expect(tournamentsApi.createTournament).toHaveBeenCalledWith(mockRequest);
    });

    it('should handle creation failure', async () => {
      const mockRequest = {
        name: 'Invalid Tournament',
        rank_tier: 'BEGINNER',
        region: 'NA',
        capacity: 4, // Invalid capacity
        format: 'Single Elimination',
        start_time: '2026-05-01T10:00:00',
        is_team_tournament: false,
        team_size: undefined,
      };

      vi.mocked(tournamentsApi.createTournament).mockRejectedValue(
        new Error('Capacity must be between 8 and 64')
      );

      const { result } = renderHook(() => useCreateTournament(), { wrapper });

      result.current.mutate(mockRequest);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should invalidate tournaments query on success', async () => {
      const mockRequest = {
        name: 'Test Tournament',
        rank_tier: 'BEGINNER',
        region: 'NA',
        capacity: 16,
        format: 'Single Elimination',
        start_time: '2026-05-01T10:00:00',
        is_team_tournament: false,
        team_size: undefined,
      };

      const mockResponse = {
        status: 'success',
        message: "Tournament 'Test Tournament' created successfully",
        tournament: {
          id: 4,
          ...mockRequest,
          status: 'UPCOMING',
          registered_count: 0,
        },
      };

      vi.mocked(tournamentsApi.createTournament).mockResolvedValue(mockResponse);

      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useCreateTournament(), { wrapper });

      result.current.mutate(mockRequest);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // NFR-14: Verify query invalidation for immediate visibility
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['tournaments'] });
    });
  });

  // useUpdateTournament hook
  describe('useUpdateTournament', () => {
    it('should update tournament successfully', async () => {
      const mockUpdated = {
        id: 1,
        name: 'Updated Cup',
        rank_tier: 'BEGINNER',
        region: 'NA',
        capacity: 16,
        registered_count: 0,
        status: 'REGISTRATION_OPEN',
        start_time: '2026-06-01T10:00:00',
        format: 'Single Elimination',
        is_team_tournament: 0,
        creator_id: 1,
        creator_username: 'testplayer',
      };

      vi.mocked(tournamentsApi.updateTournament).mockResolvedValue(mockUpdated);

      const { result } = renderHook(() => useUpdateTournament(), { wrapper });

      result.current.mutate({ id: 1, data: { name: 'Updated Cup' } });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockUpdated);
      expect(tournamentsApi.updateTournament).toHaveBeenCalledWith(1, { name: 'Updated Cup' });
    });

    it('should handle update failure', async () => {
      vi.mocked(tournamentsApi.updateTournament).mockRejectedValue(
        new Error('Only the creator can edit this tournament')
      );

      const { result } = renderHook(() => useUpdateTournament(), { wrapper });

      result.current.mutate({ id: 1, data: { name: 'Stolen' } });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should invalidate tournaments query on successful update', async () => {
      const mockUpdated = {
        id: 1,
        name: 'New Name',
        rank_tier: 'BEGINNER',
        region: 'NA',
        capacity: 16,
        registered_count: 0,
        status: 'REGISTRATION_OPEN',
        start_time: '2026-06-01T10:00:00',
        format: 'Single Elimination',
        is_team_tournament: 0,
        creator_id: 1,
      };

      vi.mocked(tournamentsApi.updateTournament).mockResolvedValue(mockUpdated);
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useUpdateTournament(), { wrapper });

      result.current.mutate({ id: 1, data: { name: 'New Name' } });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['tournaments'] });
    });
  });

  // TC-FR-001-INT: Test useRegisterTournament hook
  describe('useRegisterTournament', () => {
    it('should register player for tournament successfully', async () => {
      const playerId = 1;
      const mockRequest = {
        tournament_id: 1,
      };

      const mockResponse = {
        status: 'success',
        message: 'Successfully registered for tournament',
        tournament_id: 1,
        player_id: playerId,
      };

      vi.mocked(tournamentsApi.registerForTournament).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useRegisterTournament(), { wrapper });

      result.current.mutate({ playerId, request: mockRequest });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockResponse);
      expect(tournamentsApi.registerForTournament).toHaveBeenCalledWith(
        playerId,
        mockRequest
      );
    });

    it('should handle registration failure', async () => {
      const playerId = 1;
      const mockRequest = {
        tournament_id: 1,
      };

      vi.mocked(tournamentsApi.registerForTournament).mockRejectedValue(
        new Error('Player is not eligible for this tournament')
      );

      const { result } = renderHook(() => useRegisterTournament(), { wrapper });

      result.current.mutate({ playerId, request: mockRequest });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should invalidate tournaments query on successful registration', async () => {
      const playerId = 1;
      const mockRequest = {
        tournament_id: 1,
      };

      const mockResponse = {
        status: 'success',
        message: 'Successfully registered',
        tournament_id: 1,
        player_id: playerId,
      };

      vi.mocked(tournamentsApi.registerForTournament).mockResolvedValue(mockResponse);

      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useRegisterTournament(), { wrapper });

      result.current.mutate({ playerId, request: mockRequest });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['tournaments'] });
    });
  });
});
