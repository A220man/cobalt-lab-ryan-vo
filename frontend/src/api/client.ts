/**
 * Typed HTTP client for the Cobalt Lab backend API.
 *
 * All endpoints are documented in the OpenAPI spec served at ``/docs``.
 */
import type {
  Evaluation,
  HealthResponse,
  Job,
  Profile,
  RankingEntry,
} from '../types';

const API_BASE: string =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      detail = body?.detail ?? detail;
    } catch {
      // response body wasn't JSON
    }
    throw new ApiError(detail, resp.status);
  }
  if (resp.status === 204) return null as unknown as T;
  return resp.json();
}

export const apiClient = {
  health: () => request<HealthResponse>('/api/health'),

  getProfile: () => request<Profile>('/api/v1/profiles/default'),

  upsertProfile: (data: Partial<Profile>) =>
    request<Profile>('/api/v1/profiles/default', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  listJobs: () => request<Job[]>('/api/v1/jobs'),

  createJob: (data: Partial<Job>) =>
    request<Job>('/api/v1/jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getJob: (id: string) => request<Job>(`/api/v1/jobs/${id}`),

  evaluate: (jobId: string) =>
    request<Evaluation>('/api/v1/evaluations', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId }),
    }),

  listEvaluations: (jobId?: string) => {
    const qs = jobId ? `?job_id=${encodeURIComponent(jobId)}` : '';
    return request<Evaluation[]>(`/api/v1/evaluations${qs}`);
  },

  getRanking: () => request<RankingEntry[]>('/api/v1/ranking'),
};