// Test Case: TC-FR-013-03, Requirement: FR-13, FR-14, FR-16
// Feature: F004
// Scenario: SC007
// Frontend Unit Tests for TournamentForm Component

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TournamentForm } from './TournamentForm';

describe('TournamentForm Component', () => {
  // TC-FR-013-03: Happy Path - Form renders and submits successfully
  it('should render all form fields correctly', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    expect(screen.getByLabelText(/tournament name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/rank tier/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/region/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/capacity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/format/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start time/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/team tournament/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create tournament/i })).toBeInTheDocument();
  });

  // TC-FR-013-03: Submit valid solo tournament
  it('should submit valid solo tournament data', async () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 30);
    const futureDateString = futureDate.toISOString().slice(0, 16);

    fireEvent.change(screen.getByLabelText(/tournament name/i), {
      target: { value: 'Test Tournament' },
    });
    fireEvent.change(screen.getByLabelText(/rank tier/i), {
      target: { value: 'INTERMEDIATE' },
    });
    fireEvent.change(screen.getByLabelText(/region/i), {
      target: { value: 'EU' },
    });
    fireEvent.change(screen.getByLabelText(/capacity/i), {
      target: { value: '32' },
    });
    fireEvent.change(screen.getByLabelText(/format/i), {
      target: { value: 'Double Elimination' },
    });
    fireEvent.change(screen.getByLabelText(/start time/i), {
      target: { value: futureDateString },
    });

    fireEvent.click(screen.getByRole('button', { name: /create tournament/i }));

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith({
        name: 'Test Tournament',
        rank_tier: 'INTERMEDIATE',
        region: 'EU',
        capacity: 32,
        format: 'Double Elimination',
        start_time: futureDateString,
        is_team_tournament: false,
        team_size: undefined,
      });
    });
  });

  // TC-FR-014: Validate form has correct validation attributes
  it('should have capacity field with min and max attributes', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    const capacityInput = screen.getByLabelText(/capacity/i) as HTMLInputElement;

    expect(capacityInput).toHaveAttribute('min', '1');
    expect(capacityInput).toHaveAttribute('max', '64');
    expect(capacityInput).toHaveAttribute('type', 'number');
    expect(capacityInput).toHaveAttribute('required');
  });

  // TC-FR-014: Validate start time field
  it('should have start time field with required attribute', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    const startTimeInput = screen.getByLabelText(/start time/i) as HTMLInputElement;

    expect(startTimeInput).toHaveAttribute('type', 'datetime-local');
    expect(startTimeInput).toHaveAttribute('required');
  });

  // TC-FR-016-01: Team tournament requires team_size (verified via required attribute)
  it('should mark team_size as required for team tournaments', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    // Enable team tournament
    fireEvent.click(screen.getByLabelText(/team tournament/i));

    // Team size field should appear and be marked as required
    const teamSizeInput = screen.getByLabelText(/team size/i) as HTMLInputElement;
    expect(teamSizeInput).toBeInTheDocument();
    expect(teamSizeInput).toHaveAttribute('required');

    // This ensures HTML5 validation will prevent submission without team_size
  });

  // TC-FR-016-02: Solo tournament prohibits team_size
  it('should show and hide team_size field based on checkbox', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    expect(screen.queryByLabelText(/team size/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByLabelText(/team tournament/i));
    expect(screen.getByLabelText(/team size/i)).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText(/team tournament/i));
    expect(screen.queryByLabelText(/team size/i)).not.toBeInTheDocument();
  });

  // TC-FR-016: Team size field attributes
  it('should have team size field with correct min and max when team tournament is checked', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    fireEvent.click(screen.getByLabelText(/team tournament/i));

    const teamSizeInput = screen.getByLabelText(/team size/i) as HTMLInputElement;

    expect(teamSizeInput).toHaveAttribute('min', '2');
    expect(teamSizeInput).toHaveAttribute('max', '5');
    expect(teamSizeInput).toHaveAttribute('type', 'number');
    expect(teamSizeInput).toHaveAttribute('required');
  });

  // TC-FR-013-03: Submit valid team tournament
  it('should submit valid team tournament with team_size', async () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 30);
    const futureDateString = futureDate.toISOString().slice(0, 16);

    fireEvent.change(screen.getByLabelText(/tournament name/i), {
      target: { value: 'Team Tournament' },
    });
    fireEvent.change(screen.getByLabelText(/start time/i), {
      target: { value: futureDateString },
    });
    fireEvent.click(screen.getByLabelText(/team tournament/i));
    fireEvent.change(screen.getByLabelText(/team size/i), {
      target: { value: '5' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create tournament/i }));

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith({
        name: 'Team Tournament',
        rank_tier: 'BEGINNER',
        region: 'NA',
        capacity: 16,
        format: 'Single Elimination',
        start_time: futureDateString,
        is_team_tournament: true,
        team_size: 5,
      });
    });
  });

  // UI/UX: Loading state
  it('should disable form fields and button during loading', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} isLoading={true} />);

    expect(screen.getByLabelText(/tournament name/i)).toBeDisabled();
    expect(screen.getByLabelText(/rank tier/i)).toBeDisabled();
    expect(screen.getByLabelText(/region/i)).toBeDisabled();
    expect(screen.getByLabelText(/capacity/i)).toBeDisabled();
    expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled();
  });

  // UI/UX: Button disabled when name is empty
  it('should disable submit button when name is empty', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    const submitButton = screen.getByRole('button', { name: /create tournament/i });

    expect(submitButton).toBeDisabled();

    fireEvent.change(screen.getByLabelText(/tournament name/i), {
      target: { value: 'Test' },
    });

    expect(submitButton).not.toBeDisabled();

    fireEvent.change(screen.getByLabelText(/tournament name/i), {
      target: { value: '   ' },
    });

    expect(submitButton).toBeDisabled();
  });

  // Edit mode: initialValues prop pre-fills the form
  it('should pre-fill form fields from initialValues', () => {
    const mockOnCreate = vi.fn();
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 30);
    const futureDateString = futureDate.toISOString().slice(0, 16);

    render(
      <TournamentForm
        onCreateTournament={mockOnCreate}
        initialValues={{
          name: 'Pre-filled Cup',
          rank_tier: 'ADVANCED',
          region: 'EU',
          capacity: 32,
          format: 'Double Elimination',
          start_time: futureDateString,
          is_team_tournament: false,
        }}
      />
    );

    expect((screen.getByLabelText(/tournament name/i) as HTMLInputElement).value).toBe('Pre-filled Cup');
    expect((screen.getByLabelText(/rank tier/i) as HTMLSelectElement).value).toBe('ADVANCED');
    expect((screen.getByLabelText(/region/i) as HTMLSelectElement).value).toBe('EU');
    expect((screen.getByLabelText(/capacity/i) as HTMLInputElement).value).toBe('32');
    expect((screen.getByLabelText(/format/i) as HTMLInputElement).value).toBe('Double Elimination');
  });

  // Edit mode: submitLabel prop
  it('should show custom submitLabel on the button', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} submitLabel="Save Changes" />);

    expect(screen.getByRole('button', { name: /save changes/i })).toBeInTheDocument();
  });

  // Edit mode: submit with pre-filled data
  it('should submit form with pre-filled initialValues unchanged', async () => {
    const mockOnCreate = vi.fn();
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 30);
    const futureDateString = futureDate.toISOString().slice(0, 16);

    render(
      <TournamentForm
        onCreateTournament={mockOnCreate}
        submitLabel="Save Changes"
        initialValues={{
          name: 'Existing Cup',
          rank_tier: 'INTERMEDIATE',
          region: 'ASIA',
          capacity: 8,
          format: 'Round Robin',
          start_time: futureDateString,
          is_team_tournament: false,
        }}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => {
      expect(mockOnCreate).toHaveBeenCalledWith({
        name: 'Existing Cup',
        rank_tier: 'INTERMEDIATE',
        region: 'ASIA',
        capacity: 8,
        format: 'Round Robin',
        start_time: futureDateString,
        is_team_tournament: false,
        team_size: undefined,
      });
    });
  });

  // UI/UX: All required fields have required attribute
  it('should mark all mandatory fields as required', () => {
    const mockOnCreate = vi.fn();
    render(<TournamentForm onCreateTournament={mockOnCreate} />);

    expect(screen.getByLabelText(/tournament name/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/rank tier/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/region/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/capacity/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/format/i)).toHaveAttribute('required');
    expect(screen.getByLabelText(/start time/i)).toHaveAttribute('required');
  });
});
