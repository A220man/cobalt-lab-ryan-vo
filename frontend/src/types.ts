/**
 * Shared TypeScript types matching the backend Pydantic schemas.
 */

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface Profile {
  id: string;
  name: string;
  email: string;
  skills: string[];
  experience_years: number;
  experience_level: string;
  preferred_locations: string[];
  role_types: string[];
  dealbreakers: string[];
  remote_preference: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  source: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string[];
  extracted_skills: string[];
  experience_required: string;
  status: string;
  deadline: string | null;
  created_at: string;
  updated_at: string;
}

export interface Evaluation {
  id: string;
  job_id: string;
  profile_id: string | null;
  overall_score: number;
  dimension_scores: Record<string, number>;
  dealbreaker_hits: string[];
  skill_overlap: string[];
  skill_match_ratio: number;
  explanation: string | null;
  created_at: string;
}

export interface RankingEntry {
  job_id: string;
  job_title: string;
  job_company: string;
  job_location: string;
  overall_score: number;
  dimension_scores: Record<string, number>;
  skill_overlap: string[];
  skill_match_ratio: number;
  explanation: string | null;
  evaluation_id: string;
  created_at: string;
}

/** Form-shaped subset for profile upsert. */
export type ProfileForm = Omit<
  Profile,
  'id' | 'is_default' | 'created_at' | 'updated_at'
>;

/** Form-shaped subset for job creation. */
export type JobForm = Omit<
  Job,
  | 'id'
  | 'extracted_skills'
  | 'experience_required'
  | 'status'
  | 'deadline'
  | 'created_at'
  | 'updated_at'
>;