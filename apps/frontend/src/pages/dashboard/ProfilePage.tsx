import { FormEvent, useCallback, useEffect, useState, type JSX } from 'react';
import { Button, Input } from 'frontend-shared';

import { ApiClientError } from '../../lib/api/client';
import { getMyProfile, updateMyProfile, type ProfileWire } from '../../lib/api/profiles';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from '../Page.module.css';
import { CvUploadSection } from './CvUploadSection';

export function ProfilePage(): JSX.Element {
  const { token } = useAuth();
  const [profile, setProfile] = useState<ProfileWire | null>(null);
  const [headline, setHeadline] = useState('');
  const [bio, setBio] = useState('');
  const [skillsText, setSkillsText] = useState('');
  const [experienceYears, setExperienceYears] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await getMyProfile(token);
      setProfile(data);
      setHeadline(data.headline ?? '');
      setBio(data.bio ?? '');
      setSkillsText((data.skills ?? []).join(', '));
      setExperienceYears(
        data.experience_years === null || data.experience_years === undefined
          ? ''
          : String(data.experience_years),
      );
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load profile.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onSave(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!token) {
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(null);
    const skills = skillsText
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    let years: number | null = null;
    if (experienceYears.trim() !== '') {
      const n = Number(experienceYears);
      if (!Number.isFinite(n) || n < 0) {
        setError('Experience years must be a non-negative number.');
        setSaving(false);
        return;
      }
      years = Math.floor(n);
    }
    try {
      const updated = await updateMyProfile(token, {
        headline: headline.trim() || null,
        bio: bio.trim() || null,
        skills,
        experience_years: years,
      });
      setProfile(updated);
      setSuccess('Profile saved.');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to save profile.');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <section className={styles.page}>
        <h1>Profile</h1>
        <p className={styles.muted} role="status">
          Loading profile…
        </p>
      </section>
    );
  }

  return (
    <section className={styles.page}>
      <h1>Profile</h1>
      <p className={styles.lead}>
        Update how your digital twin presents your professional background.
      </p>
      {profile && (
        <p className={styles.muted}>
          CV on file: {profile.has_cv ? 'yes' : 'no'}
          {profile.has_extracted_text ? ' · text extracted' : ''}
        </p>
      )}
      {token && <CvUploadSection token={token} profile={profile} onProfileRefresh={setProfile} />}
      <form className={styles.formWide} onSubmit={(e) => void onSave(e)}>
        <Input
          label="Headline"
          value={headline}
          onChange={(ev) => setHeadline(ev.target.value)}
          helperText="Short professional title shown to visitors."
        />
        <label className={styles.textAreaField}>
          <span className={styles.textAreaLabel}>Bio</span>
          <textarea
            className={styles.textarea}
            value={bio}
            onChange={(ev) => setBio(ev.target.value)}
            rows={5}
            maxLength={10_000}
          />
        </label>
        <Input
          label="Skills"
          value={skillsText}
          onChange={(ev) => setSkillsText(ev.target.value)}
          helperText="Comma-separated list (e.g. Python, FastAPI, React)."
        />
        <Input
          label="Years of experience"
          type="number"
          min={0}
          max={80}
          value={experienceYears}
          onChange={(ev) => setExperienceYears(ev.target.value)}
        />
        {error && (
          <p className={styles.formError} role="alert">
            {error}
          </p>
        )}
        {success && (
          <p className={styles.formSuccess} role="status">
            {success}
          </p>
        )}
        <Button type="submit" isLoading={saving}>
          Save profile
        </Button>
      </form>
    </section>
  );
}
