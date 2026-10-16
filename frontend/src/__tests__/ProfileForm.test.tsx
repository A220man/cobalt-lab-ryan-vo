import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProfileForm from '../components/ProfileForm';
import type { Profile } from '../types';

const mockProfile: Profile = {
  id: 'profile-1',
  name: 'Test User',
  email: 'test@test.com',
  skills: ['python', 'docker'],
  experience_years: 5,
  experience_level: 'senior',
  preferred_locations: ['New York, NY'],
  role_types: ['ml engineer'],
  dealbreakers: ['on-call'],
  remote_preference: 'preferred',
  is_default: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('ProfileForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form fields pre-filled with profile data', () => {
    render(
      <ProfileForm
        profile={mockProfile}
        onSubmit={mockOnSubmit}
        saving={false}
      />,
    );
    expect(screen.getByLabelText(/name/i)).toHaveValue('Test User');
    expect(screen.getByLabelText(/email/i)).toHaveValue('test@test.com');
    expect(screen.getByLabelText(/skills/i)).toHaveValue('python, docker');
    expect(screen.getByLabelText(/experience level/i)).toHaveValue('senior');
  });

  it('calls onSubmit with converted form data on submit', async () => {
    render(
      <ProfileForm
        profile={mockProfile}
        onSubmit={mockOnSubmit}
        saving={false}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    });
    const submitted = mockOnSubmit.mock.calls[0][0];
    expect(submitted.name).toBe('Test User');
    expect(submitted.email).toBe('test@test.com');
    expect(submitted.skills).toEqual(['python', 'docker']);
  });

  it('renders an empty form when no profile is provided', () => {
    render(
      <ProfileForm
        profile={null}
        onSubmit={mockOnSubmit}
        saving={false}
      />,
    );
    expect(screen.getByLabelText(/name/i)).toHaveValue('');
    expect(screen.getByLabelText(/skills/i)).toHaveValue('');
  });

  it('disables form fields while saving', () => {
    render(
      <ProfileForm
        profile={mockProfile}
        onSubmit={mockOnSubmit}
        saving={true}
      />,
    );
    expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled();
  });
});