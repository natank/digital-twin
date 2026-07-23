import { FormEvent, useCallback, useEffect, useState, type JSX } from 'react';
import { Link } from 'react-router-dom';
import { Button, Input } from 'frontend-shared';

import { ApiClientError } from '../../lib/api/client';
import {
  deletePushoverConfig,
  getNotificationPreferences,
  getPushoverConfig,
  sendTestNotification,
  updateNotificationPreferences,
  updatePushoverConfig,
  type NotificationPreferencesWire,
  type PushoverConfigWire,
} from '../../lib/api/notifications';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from '../Page.module.css';

export function PushoverPage(): JSX.Element {
  const { token } = useAuth();
  const [config, setConfig] = useState<PushoverConfigWire | null>(null);
  const [prefs, setPrefs] = useState<NotificationPreferencesWire | null>(null);
  const [userKey, setUserKey] = useState('');
  const [device, setDevice] = useState('');
  const [sound, setSound] = useState('pushover');
  const [enabled, setEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const [c, p] = await Promise.all([
        getPushoverConfig(token),
        getNotificationPreferences(token),
      ]);
      setConfig(c);
      setPrefs(p);
      setEnabled(c.enabled);
      setDevice(c.device ?? '');
      setSound(c.sound ?? 'pushover');
      setUserKey('');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load Pushover config.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onSave(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!token) return;
    if (userKey.trim().length < 8 && !config?.configured) {
      setError('Enter a valid Pushover user key (at least 8 characters).');
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const key = userKey.trim() || 'unchanged-placeholder-key';
      // Backend requires user_key on PUT; when already configured and key empty, re-send masked path is not supported — require key.
      if (userKey.trim().length < 8) {
        setError('Re-enter your Pushover user key to update settings (keys are not returned).');
        setSaving(false);
        return;
      }
      const updated = await updatePushoverConfig(token, {
        user_key: key,
        device: device.trim() || null,
        sound: sound.trim() || 'pushover',
        enabled,
      });
      setConfig(updated);
      setUserKey('');
      setSuccess('Pushover settings saved.');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to save Pushover settings.');
    } finally {
      setSaving(false);
    }
  }

  async function onRemove(): Promise<void> {
    if (!token) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await deletePushoverConfig(token);
      setConfig({
        configured: false,
        enabled: false,
        device: null,
        sound: null,
        user_key_masked: null,
      });
      setSuccess('Pushover configuration removed.');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to remove config.');
    } finally {
      setSaving(false);
    }
  }

  async function onTest(): Promise<void> {
    if (!token) return;
    setTesting(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await sendTestNotification(token);
      setSuccess(`Test sent (${result.delivery_status}): ${result.message}`);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Test notification failed.');
    } finally {
      setTesting(false);
    }
  }

  async function onToggleGlobalPush(value: boolean): Promise<void> {
    if (!token || !prefs) return;
    try {
      const updated = await updateNotificationPreferences(token, {
        global_push_enabled: value,
      });
      setPrefs(updated);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to update preferences.');
    }
  }

  if (loading) {
    return (
      <section className={styles.page}>
        <h1>Pushover</h1>
        <p className={styles.muted}>Loading…</p>
      </section>
    );
  }

  return (
    <section className={styles.page}>
      <h1>Pushover setup</h1>
      <p className={styles.lead}>
        Receive push alerts on your phone when visitors engage your twin. Create a free account at{' '}
        <a href="https://pushover.net" target="_blank" rel="noreferrer">
          pushover.net
        </a>{' '}
        and paste your <strong>user key</strong> here.
      </p>
      <p className={styles.muted}>
        <Link to="/dashboard/notifications">← Back to notifications</Link>
      </p>

      <section className={styles.panel}>
        <h2>Status</h2>
        <p className={styles.muted}>
          {config?.configured
            ? `Configured (${config.user_key_masked ?? 'key set'}) · ${
                config.enabled ? 'enabled' : 'disabled'
              }`
            : 'Not configured'}
        </p>
        {prefs && (
          <label className={styles.checkRow}>
            <input
              type="checkbox"
              checked={prefs.global_push_enabled}
              onChange={(ev) => void onToggleGlobalPush(ev.target.checked)}
            />
            Global push enabled
          </label>
        )}
      </section>

      <form className={styles.formWide} onSubmit={(e) => void onSave(e)}>
        <Input
          label="User key"
          value={userKey}
          onChange={(ev) => setUserKey(ev.target.value)}
          autoComplete="off"
          helperText={
            config?.configured
              ? `Currently ${config.user_key_masked}. Re-enter key to change.`
              : 'From your Pushover dashboard.'
          }
        />
        <Input
          label="Device (optional)"
          value={device}
          onChange={(ev) => setDevice(ev.target.value)}
          helperText="Leave blank to notify all devices."
        />
        <Input
          label="Sound"
          value={sound}
          onChange={(ev) => setSound(ev.target.value)}
          helperText="Default: pushover"
        />
        <label className={styles.checkRow}>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(ev) => setEnabled(ev.target.checked)}
          />
          Enable push for this account
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
            Save
          </Button>
          <Button
            type="button"
            variant="secondary"
            isLoading={testing}
            disabled={!config?.configured}
            onClick={() => void onTest()}
          >
            Send test
          </Button>
          {config?.configured && (
            <Button
              type="button"
              variant="danger"
              disabled={saving}
              onClick={() => void onRemove()}
            >
              Remove config
            </Button>
          )}
        </div>
      </form>
    </section>
  );
}
