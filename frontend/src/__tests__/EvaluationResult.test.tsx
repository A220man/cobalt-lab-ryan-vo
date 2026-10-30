import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import EvaluationResult from '../components/EvaluationResult';
import type { Evaluation } from '../types';

const makeEvaluation = (
  overrides: Partial<Evaluation> = {},
): Evaluation => ({
  id: 'eval-1',
  job_id: 'job-1',
  profile_id: 'profile-1',
  overall_score: 0.85,
  dimension_scores: {
    skills: 1.0,
    experience: 0.8,
    location: 0.7,
    role_type: 1.0,
    dealbreakers: 1.0,
  },
  dealbreaker_hits: [],
  skill_overlap: ['python', 'docker'],
  skill_match_ratio: 0.67,
  explanation: 'Good match overall.',
  created_at: '2026-01-01T00:00:00Z',
  ...overrides,
});

describe('EvaluationResult', () => {
  it('displays the overall score as a percentage', () => {
    render(<EvaluationResult evaluation={makeEvaluation()} />);
    expect(screen.getByText('Fit Score: 85%')).toBeInTheDocument();
  });

  it('renders dimension scores in a table', () => {
    render(<EvaluationResult evaluation={makeEvaluation()} />);
    expect(screen.getByText('skills')).toBeInTheDocument();
    expect(screen.getByText('dealbreakers')).toBeInTheDocument();
  });

  it('shows skills matched', () => {
    render(<EvaluationResult evaluation={makeEvaluation()} />);
    expect(screen.getByText(/Skills matched/)).toBeInTheDocument();
    expect(screen.getByText('python, docker')).toBeInTheDocument();
  });

  it('shows dealbreaker hits when present', () => {
    render(
      <EvaluationResult
        evaluation={makeEvaluation({ dealbreaker_hits: ['on-call'] })}
      />,
    );
    expect(screen.getByText(/Dealbreakers hit/)).toBeInTheDocument();
    expect(screen.getByText('on-call')).toBeInTheDocument();
  });

  it('omits dealbreaker section when no hits', () => {
    const { container } = render(
      <EvaluationResult evaluation={makeEvaluation()} />,
    );
    expect(
      container.querySelector('.dealbreaker-hits'),
    ).toBeNull();
  });

  it('renders dimensions in fixed order: skills, experience, location, role_type, dealbreakers', () => {
    render(<EvaluationResult evaluation={makeEvaluation()} />);
    const rows = screen.getAllByRole('row');
    // rows[0] is header, rows[1-5] are dimension rows
    expect(rows[1]).toHaveTextContent('skills');
    expect(rows[2]).toHaveTextContent('experience');
    expect(rows[3]).toHaveTextContent('location');
    expect(rows[4]).toHaveTextContent('role_type');
    expect(rows[5]).toHaveTextContent('dealbreakers');
  });

  it('omits dimensions not present in dimension_scores', () => {
    render(
      <EvaluationResult
        evaluation={makeEvaluation({
          dimension_scores: { skills: 0.5, location: 0.8 },
        })}
      />,
    );
    const rows = screen.getAllByRole('row');
    // Only skills and location should appear
    expect(rows).toHaveLength(3); // header + 2 dimensions
    expect(rows[1]).toHaveTextContent('skills');
    expect(rows[2]).toHaveTextContent('location');
  });
});