import { apiClient } from '../api/client';
import { useState } from 'react';
import type { Job, JobForm } from '../types';

interface Props {
  onJobCreated: (job: Job) => void;
}

export default function JobForm({ onJobCreated }: Props) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    source: '',
    title: '',
    company: '',
    location: '',
    description: '',
    requirements: '',
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const data: JobForm = {
        source: formData.source,
        title: formData.title,
        company: formData.company,
        location: formData.location,
        description: formData.description,
        requirements: formData.requirements
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      };
      const job = await apiClient.createJob(data);
      onJobCreated(job);
      setFormData({
        source: '',
        title: '',
        company: '',
        location: '',
        description: '',
        requirements: '',
      });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="job-form" onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="source">Source URL</label>
          <input
            id="source"
            name="source"
            type="url"
            placeholder="https://example.com/job"
            value={formData.source}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            type="text"
            placeholder="Senior ML Engineer"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="company">Company</label>
          <input
            id="company"
            name="company"
            type="text"
            placeholder="Acme Corp"
            value={formData.company}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-field">
          <label htmlFor="location">Location</label>
          <input
            id="location"
            name="location"
            type="text"
            placeholder="New York, NY (or Remote)"
            value={formData.location}
            onChange={handleChange}
          />
        </div>

        <div className="form-field">
          <label htmlFor="requirements">
            Requirements (comma-separated)
          </label>
          <input
            id="requirements"
            name="requirements"
            type="text"
            placeholder="Python, PyTorch, Docker"
            value={formData.requirements}
            onChange={handleChange}
          />
        </div>

        <div className="form-field full-width">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            placeholder="Paste the job description here..."
            value={formData.description}
            onChange={handleChange}
            rows={6}
          />
        </div>
      </div>

      <button type="submit" disabled={submitting} className="btn-primary">
        {submitting ? 'Creating…' : 'Create Job'}
      </button>
    </form>
  );
}