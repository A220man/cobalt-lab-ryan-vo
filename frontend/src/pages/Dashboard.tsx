import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import JobForm from '../components/JobForm';
import EvaluationResult from '../components/EvaluationResult';
import type { Evaluation, Job, RankingEntry } from '../types';

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [ranking, setRanking] = useState<RankingEntry[]>([]);
  const [evaluations, setEvaluations] = useState<Record<string, Evaluation>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [evaluatingJobId, setEvaluatingJobId] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
    loadRanking();
  }, []);

  async function loadJobs() {
    try {
      const data = await apiClient.listJobs();
      setJobs(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function loadRanking() {
    try {
      const data = await apiClient.getRanking();
      setRanking(data);
    } catch {
      // Ranking may be empty if no evaluations exist yet
    }
  }

  async function handleEvaluate(jobId: string) {
    setEvaluatingJobId(jobId);
    try {
      const result = await apiClient.evaluate(jobId);
      setEvaluations((prev) => ({ ...prev, [jobId]: result }));
      await loadRanking();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setEvaluatingJobId(null);
    }
  }

  function handleJobCreated(job: Job) {
    setJobs((prev) => [job, ...prev]);
  }

  if (loading) {
    return <div className="loading">Loading jobs…</div>;
  }

  return (
    <div className="dashboard">
      <JobForm onJobCreated={handleJobCreated} />

      {error && <div className="error">{error}</div>}

      <section className="job-list-section">
        <h2>Jobs</h2>
        {jobs.length === 0 ? (
          <p className="empty">No jobs yet. Submit one above.</p>
        ) : (
          <ul className="job-list">
            {jobs.map((job) => (
              <li key={job.id} className="job-card">
                <div className="job-info">
                  <h3>{job.title}</h3>
                  <p className="company">{job.company}</p>
                  <p className="location">{job.location}</p>
                  <span className={`status status-${job.status}`}>
                    {job.status}
                  </span>
                </div>

                {job.status === 'new' && (
                  <button
                    onClick={() => handleEvaluate(job.id)}
                    disabled={!!evaluatingJobId}
                    className="btn-secondary"
                  >
                    {evaluatingJobId === job.id ? 'Evaluating…' : 'Evaluate'}
                  </button>
                )}

                {evaluations[job.id] && (
                  <EvaluationResult evaluation={evaluations[job.id]} />
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      {ranking.length > 0 && (
        <section className="ranking-section">
          <h2>Ranked Jobs</h2>
          <table className="ranking-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Score</th>
                <th>Job</th>
                <th>Company</th>
                <th>Skills</th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((entry, idx) => (
                <tr key={entry.evaluation_id}>
                  <td>{idx + 1}</td>
                  <td>{Math.round(entry.overall_score * 100)}%</td>
                  <td>{entry.job_title}</td>
                  <td>{entry.job_company}</td>
                  <td>{Math.round(entry.skill_match_ratio * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}