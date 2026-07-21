import { FormEvent, useCallback, useEffect, useState, type JSX } from 'react';
import { Button } from 'frontend-shared';

import { ApiClientError } from '../../lib/api/client';
import {
  getMySummary,
  regenerateMySummary,
  updateMySummary,
  type ProfileSummaryWire,
} from '../../lib/api/profiles';
import styles from '../Page.module.css';

export interface SummarySectionProps {
  token: string;
}

function pretty(summary: Record<string, unknown> | null): string {
  if (!summary) {
    return '{\n  \n}';
  }
  try {
    return JSON.stringify(summary, null, 2);
  } catch {
    return '{}';
  }
}

export function SummarySection({ token }: SummarySectionProps): JSX.Element {
  const [data, setData] = useState<ProfileSummaryWire | null>(null);
  const [editor, setEditor] = useState('{}');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const summary = await getMySummary(token);
      setData(summary);
      setEditor(pretty(summary.profile_summary));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load summary.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onSave(e: FormEvent): Promise<void> {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(editor) as Record<string, unknown>;
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Summary must be a JSON object');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid JSON');
      setSaving(false);
      return;
    }
    try {
      const updated = await updateMySummary(token, {
        profile_summary: parsed,
        skills: data?.skills ?? undefined,
        experience_years: data?.experience_years ?? undefined,
      });
      setData(updated);
      setEditor(pretty(updated.profile_summary));
      setSuccess('Summary saved.');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to save summary.');
    } finally {
      setSaving(false);
    }
  }

  async function onRegenerate(): Promise<void> {
    setRegenerating(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await regenerateMySummary(token);
      setData(updated);
      setEditor(pretty(updated.profile_summary));
      setSuccess('Summary regenerated from CV text.');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Regeneration failed.');
    } finally {
      setRegenerating(false);
    }
  }

  if (loading) {
    return (
      <section className={styles.panel}>
        <h2>Profile summary</h2>
        <p className={styles.muted}>Loading summary…</p>
      </section>
    );
  }

  return (
    <section className={styles.panel} aria-labelledby="summary-heading">
      <h2 id="summary-heading">Profile summary</h2>
      <p className={styles.muted}>
        Structured AI summary used by the twin. Edit JSON carefully, or regenerate from extracted CV
        text.
      </p>
      <form className={styles.formWide} onSubmit={(e) => void onSave(e)}>
        <label className={styles.textAreaField}>
          <span className={styles.textAreaLabel}>Summary JSON</span>
          <textarea
            className={styles.textarea}
            value={editor}
            onChange={(ev) => setEditor(ev.target.value)}
            rows={12}
            spellCheck={false}
            aria-label="Summary JSON"
          />
        </label>
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
        <div className={styles.actions}>
          <Button type="submit" isLoading={saving}>
            Save summary
          </Button>
          <Button
            type="button"
            variant="secondary"
            isLoading={regenerating}
            onClick={() => void onRegenerate()}
          >
            Regenerate from CV
          </Button>
        </div>
      </form>
    </section>
  );
}
