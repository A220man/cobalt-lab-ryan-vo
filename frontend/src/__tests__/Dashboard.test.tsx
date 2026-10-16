import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';
import { apiClient } from '../api/client';

vi.mock('../api/client', () => ({
  apiClient: {
    listJobs: vi.fn(),
    getRanking: vi.fn(),
    evaluate: vi.fn(),
    createJob: vi.fn(),
    health: vi.fn(),
    getProfile: vi.fn(),
    upsertProfile: vi.fn(),
    getJob: vi.fn(),
    listEvaluations: vi.fn(),
  },
}));

const makeJob = (overrides: Partial<any> = {}) => ({
  id: 'job-1',
  source: 'https://example.com/job',
  title: 'ML Engineer',
  company: 'Acme Corp',
  location: 'New York, NY',
  description: 'Senior ML role on-call',
  requirements: ['Python', 'PyTorch'],
  extracted_skills: ['python', 'pytorch'],
  experience_required: 'senior',
  status: 'new',
  deadline: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  ...overrides,
});

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiClient.listJobs).mockResolvedValue([]);
    vi.mocked(apiClient.getRanking).mockResolvedValue([]);
  });

  it('shows loading state initially', async () => {
    render(<Dashboard />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it('renders job cards after loading', async () => {
    vi.mocked(apiClient.listJobs).mockResolvedValue([makeJob()]);
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText('ML Engineer')).toBeInTheDocument();
    });
  });

  it('shows empty state when no jobs exist', async () => {
    vi.mocked(apiClient.listJobs).mockResolvedValue([]);
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/no jobs/i)).toBeInTheDocument();
    });
  });

  it('shows evaluate button for new jobs', async () => {
    vi.mocked(apiClient.listJobs).mockResolvedValue([makeJob()]);
    render(<Dashboard />);
    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: /evaluate/i }),
      ).toBeInTheDocument();
    });
  });
});