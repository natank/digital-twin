import { FormEvent, useCallback, useEffect, useState, type JSX } from 'react';
import { Button, Input } from 'frontend-shared';

import { ApiClientError } from '../../lib/api/client';
import {
  getTwinConfig,
  listPromptVersions,
  previewSystemPrompt,
  restorePromptVersion,
  updateTwinConfig,
  type PromptVersionWire,
  type TwinConfigWire,
} from '../../lib/api/config';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from '../Page.module.css';

const TONES = ['professional', 'friendly', 'casual', 'formal'] as const;
const LENGTHS = ['concise', 'balanced', 'detailed'] as const;

export function ConfigPage(): JSX.Element {
  const { token } = useAuth();
  const [config, setConfig] = useState<TwinConfigWire | null>(null);
  const [versions, setVersions] = useState<PromptVersionWire[]>([]);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [tone, setTone] = useState('professional');
  const [responseLength, setResponseLength] = useState('balanced');
  const [allowedTopics, setAllowedTopics] = useState('');
  const [forbiddenTopics, setForbiddenTopics] = useState('');
  const [brand, setBrand] = useState('');
  const [sampleQ, setSampleQ] = useState('What is your professional background?');
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const applyConfig = useCallback((c: TwinConfigWire): void => {
    setConfig(c);
    setSystemPrompt(c.system_prompt);
    setTone(c.tone);
    setResponseLength(c.response_length);
    setAllowedTopics((c.allowed_topics ?? []).join(', '));
    setForbiddenTopics((c.forbidden_topics ?? []).join(', '));
    setBrand(c.brand_guidelines ?? '');
  }, []);

  const load = useCallback(async (): Promise<void> => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [c, v] = await Promise.all([getTwinConfig(token), listPromptVersions(token)]);
      applyConfig(c);
      setVersions(v.versions);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load config.');
    } finally {
      setLoading(false);
    }
  }, [token, applyConfig]);

  useEffect(() => {
    void load();
  }, [load]);

  function parseTopics(raw: string): string[] {
    return raw
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  }

  async function onSave(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await updateTwinConfig(token, {
        system_prompt: systemPrompt,
        tone,
        response_length: responseLength,
        allowed_topics: parseTopics(allowedTopics),
        forbidden_topics: parseTopics(forbiddenTopics),
        brand_guidelines: brand.trim() || null,
      });
      applyConfig(updated);
      const v = await listPromptVersions(token);
      setVersions(v.versions);
      setSuccess('Twin configuration saved.');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to save config.');
    } finally {
      setSaving(false);
    }
  }

  async function onPreview(): Promise<void> {
    if (!token) return;
    setError(null);
    try {
      const result = await previewSystemPrompt(token, {
        system_prompt: systemPrompt,
        sample_question: sampleQ,
      });
      setPreview(
        `Rendered prompt (excerpt):\n${result.rendered_system_prompt.slice(0, 800)}\n\nSample reply:\n${result.sample_reply}`,
      );
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Preview failed.');
    }
  }

  async function onRestore(version: number): Promise<void> {
    if (!token) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await restorePromptVersion(token, version);
      await load();
      setSuccess(`Restored prompt version ${version}.`);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Restore failed.');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <section className={styles.page}>
        <h1>Twin config</h1>
        <p className={styles.muted}>Loading…</p>
      </section>
    );
  }

  return (
    <section className={styles.page}>
      <h1>Twin config</h1>
      <p className={styles.lead}>
        Customize the system prompt, tone, and topic boundaries used by chat. Placeholders:{' '}
        <code>{'{owner_name}'}</code>, <code>{'{profile_summary}'}</code>.
      </p>

      <form className={styles.formWide} onSubmit={(e) => void onSave(e)}>
        <label className={styles.textAreaField}>
          <span className={styles.textAreaLabel}>System prompt</span>
          <textarea
            className={styles.textarea}
            value={systemPrompt}
            onChange={(ev) => setSystemPrompt(ev.target.value)}
            rows={10}
            spellCheck={false}
            aria-label="System prompt"
          />
        </label>

        <label className={styles.textAreaField}>
          <span className={styles.textAreaLabel}>Tone</span>
          <select
            className={styles.textarea}
            value={tone}
            onChange={(ev) => setTone(ev.target.value)}
            aria-label="Tone"
          >
            {TONES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>

        <label className={styles.textAreaField}>
          <span className={styles.textAreaLabel}>Response length</span>
          <select
            className={styles.textarea}
            value={responseLength}
            onChange={(ev) => setResponseLength(ev.target.value)}
            aria-label="Response length"
          >
            {LENGTHS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>

        <Input
          label="Allowed topics"
          value={allowedTopics}
          onChange={(ev) => setAllowedTopics(ev.target.value)}
          helperText="Comma-separated. Empty = no restriction."
        />
        <Input
          label="Forbidden topics"
          value={forbiddenTopics}
          onChange={(ev) => setForbiddenTopics(ev.target.value)}
          helperText="Comma-separated boundaries."
        />
        <label className={styles.textAreaField}>
          <span className={styles.textAreaLabel}>Brand guidelines</span>
          <textarea
            className={styles.textarea}
            value={brand}
            onChange={(ev) => setBrand(ev.target.value)}
            rows={3}
            aria-label="Brand guidelines"
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
            Save config
          </Button>
        </div>
      </form>

      <section className={styles.panel}>
        <h2>Preview</h2>
        <Input
          label="Sample question"
          value={sampleQ}
          onChange={(ev) => setSampleQ(ev.target.value)}
        />
        <Button type="button" variant="secondary" onClick={() => void onPreview()}>
          Preview prompt
        </Button>
        {preview && (
          <pre className={styles.muted} style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
            {preview}
          </pre>
        )}
      </section>

      <section className={styles.panel}>
        <h2>Prompt versions</h2>
        {versions.length === 0 ? (
          <p className={styles.muted}>No versions yet — save a prompt to create history.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {versions.map((v) => (
              <li
                key={v.version_number}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  gap: '0.75rem',
                  padding: '0.4rem 0',
                  borderBottom: '1px solid #e2e8f0',
                }}
              >
                <span>
                  v{v.version_number}
                  {v.created_at ? ` · ${new Date(v.created_at).toLocaleString()}` : ''}
                </span>
                <Button
                  type="button"
                  size="small"
                  variant="secondary"
                  onClick={() => void onRestore(v.version_number)}
                >
                  Restore
                </Button>
              </li>
            ))}
          </ul>
        )}
        {config && (
          <p className={styles.muted} style={{ marginTop: '0.75rem' }}>
            Config id: {config.id.slice(0, 8)}…
          </p>
        )}
      </section>
    </section>
  );
}
