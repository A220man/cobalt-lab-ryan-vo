import { useEffect, useState } from 'react';
import type { Profile, ProfileForm } from '../types';

interface Props {
  profile: Profile | null;
  onSubmit: (data: ProfileForm) => Promise<void>;
  saving: boolean;
}

const EXPERIENCE_LEVELS = [
  'entry',
  'junior',
  'mid',
  'senior',
  'lead',
  'principal',
];

const REMOTE_PREFERENCES = ['required', 'preferred', 'optional', 'no'];

export default function ProfileForm({ profile, onSubmit, saving }: Props) {
  const [formData, setFormData] = useState({
    name: profile?.name ?? '',
    email: profile?.email ?? '',
    skills: profile?.skills.join(', ') ?? '',
    experience_years: profile?.experience_years ?? 0,
    experience_level: profile?.experience_level ?? 'mid',
    preferred_locations: profile?.preferred_locations.join(', ') ?? '',
    role_types: profile?.role_types.join(', ') ?? '',
    dealbreakers: profile?.dealbreakers.join(', ') ?? '',
    remote_preference: profile?.remote_preference ?? 'preferred',
  });

  // Re-initialise when the profile prop changes (e.g. after a fetch)
  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name,
        email: profile.email,
        skills: profile.skills.join(', '),
        experience_years: profile.experience_years,
        experience_level: profile.experience_level,
        preferred_locations: profile.preferred_locations.join(', '),
        role_types: profile.role_types.join(', '),
        dealbreakers: profile.dealbreakers.join(', '),
        remote_preference: profile.remote_preference,
      });
    }
  }, [profile]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      name: formData.name,
      email: formData.email,
      skills: formData.skills
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      experience_years: parseInt(String(formData.experience_years), 10) || 0,
      experience_level: formData.experience_level,
      preferred_locations: formData.preferred_locations
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      role_types: formData.role_types
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      dealbreakers: formData.dealbreakers
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      remote_preference: formData.remote_preference,
    });
  };

  return (
    <form className="profile-form" onSubmit={handleSubmit}>
      <fieldset disabled={saving}>
        <legend>Profile</legend>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="skills">Skills (comma-separated)</label>
            <input
              id="skills"
              name="skills"
              type="text"
              placeholder="python, docker, aws"
              value={formData.skills}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="experience_years">Years of experience</label>
            <input
              id="experience_years"
              name="experience_years"
              type="number"
              min="0"
              value={formData.experience_years}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="experience_level">Experience level</label>
            <select
              id="experience_level"
              name="experience_level"
              value={formData.experience_level}
              onChange={handleChange}
            >
              {EXPERIENCE_LEVELS.map((lvl) => (
                <option key={lvl} value={lvl}>
                  {lvl}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="preferred_locations">Preferred locations</label>
            <input
              id="preferred_locations"
              name="preferred_locations"
              type="text"
              placeholder="New York, Remote"
              value={formData.preferred_locations}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="role_types">Role types</label>
            <input
              id="role_types"
              name="role_types"
              type="text"
              placeholder="ml engineer, backend engineer"
              value={formData.role_types}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="dealbreakers">Dealbreakers</label>
            <input
              id="dealbreakers"
              name="dealbreakers"
              type="text"
              placeholder="on-call, visa sponsorship"
              value={formData.dealbreakers}
              onChange={handleChange}
            />
          </div>

          <div className="form-field">
            <label htmlFor="remote_preference">Remote preference</label>
            <select
              id="remote_preference"
              name="remote_preference"
              value={formData.remote_preference}
              onChange={handleChange}
            >
              {REMOTE_PREFERENCES.map((rp) => (
                <option key={rp} value={rp}>
                  {rp}
                </option>
              ))}
            </select>
          </div>
        </div>
      </fieldset>

      <button type="submit" disabled={saving} className="btn-primary">
        {saving ? 'Saving…' : 'Save Profile'}
      </button>
    </form>
  );
}