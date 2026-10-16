import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import ProfileForm from '../components/ProfileForm';
import type { Profile, ProfileForm as ProfileFormType } from '../types';

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const data = await apiClient.getProfile();
      setProfile(data);
    } catch {
      // 404 means no profile exists yet -- show empty form
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(data: ProfileFormType) {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const saved = await apiClient.upsertProfile(data);
      setProfile(saved);
      setSuccess(true);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="loading">Loading profile…</div>;
  }

  return (
    <div className="profile-page">
      <h1>Profile</h1>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Profile saved!</div>}
      <ProfileForm
        profile={profile}
        onSubmit={handleSubmit}
        saving={saving}
      />
    </div>
  );
}