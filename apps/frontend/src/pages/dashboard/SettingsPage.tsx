import { FormEvent, useState, type JSX } from 'react';
import { Link } from 'react-router-dom';
import { Button, Input, isValidEmail } from 'frontend-shared';

import { forgotPasswordRequest } from '../../lib/api/auth';
import { ApiClientError } from '../../lib/api/client';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from '../Page.module.css';

const PREFS_KEY = 'dt_owner_prefs';

interface OwnerPrefs {
  emailDigest: boolean;
  productUpdates: boolean;
}

function loadPrefs(): OwnerPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (!raw) {
      return { emailDigest: true, productUpdates: false };
    }
    return { emailDigest: true, productUpdates: false, ...JSON.parse(raw) };
  } catch {
    return { emailDigest: true, productUpdates: false };
  }
}

export function SettingsPage(): JSX.Element {
  const { owner, logout } = useAuth();
  const [prefs, setPrefs] = useState<OwnerPrefs>(() => loadPrefs());
  const [resetBusy, setResetBusy] = useState(false);
  const [resetMsg, setResetMsg] = useState<string | null>(null);
  const [resetErr, setResetErr] = useState<string | null>(null);
  const [prefsSaved, setPrefsSaved] = useState(false);

  async function onRequestPasswordReset(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!owner?.email || !isValidEmail(owner.email)) {
      setResetErr('No valid account email on session.');
      return;
    }
    setResetBusy(true);
    setResetErr(null);
    setResetMsg(null);
    try {
      await forgotPasswordRequest(owner.email);
      setResetMsg(
        'If the account exists, a reset email was sent (check server logs in local dev). Use the link to set a new password.',
      );
    } catch (err) {
      setResetErr(err instanceof ApiClientError ? err.message : 'Request failed.');
    } finally {
      setResetBusy(false);
    }
  }

  function onSavePrefs(e: FormEvent): void {
    e.preventDefault();
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    setPrefsSaved(true);
  }

  return (
    <section className={styles.page}>
      <h1>Settings</h1>
      <p className={styles.lead}>Manage account details and basic preferences.</p>

      <section className={styles.panel} aria-labelledby="account-heading">
        <h2 id="account-heading">Account</h2>
        <dl className={styles.metaList}>
          <div>
            <dt>Name</dt>
            <dd>{owner ? `${owner.first_name} ${owner.last_name}`.trim() : '—'}</dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{owner?.email ?? '—'}</dd>
          </div>
          <div>
            <dt>Email verified</dt>
            <dd>{owner?.email_verified ? 'Yes' : 'No'}</dd>
          </div>
          <div>
            <dt>Owner ID</dt>
            <dd>
              <code>{owner?.id ?? '—'}</code>
            </dd>
          </div>
        </dl>
      </section>

      <section className={styles.panel} aria-labelledby="password-heading">
        <h2 id="password-heading">Password</h2>
        <p className={styles.muted}>
          Password changes use the email reset flow (no in-app current-password API in MVP). You can
          also open the public <Link to="/forgot-password">forgot password</Link> page.
        </p>
        <form onSubmit={(e) => void onRequestPasswordReset(e)}>
          <Input label="Account email" value={owner?.email ?? ''} readOnly />
          {resetErr && (
            <p className={styles.formError} role="alert">
              {resetErr}
            </p>
          )}
          {resetMsg && (
            <p className={styles.formSuccess} role="status">
              {resetMsg}
            </p>
          )}
          <div className={styles.actions}>
            <Button type="submit" isLoading={resetBusy}>
              Email password reset link
            </Button>
          </div>
        </form>
      </section>

      <section className={styles.panel} aria-labelledby="prefs-heading">
        <h2 id="prefs-heading">Preferences</h2>
        <p className={styles.muted}>
          Client-only preferences for the MVP (stored in this browser). Server-backed prefs land
          with notifications in Week 14.
        </p>
        <form className={styles.formWide} onSubmit={onSavePrefs}>
          <label className={styles.checkRow}>
            <input
              type="checkbox"
              checked={prefs.emailDigest}
              onChange={(ev) => setPrefs((p) => ({ ...p, emailDigest: ev.target.checked }))}
            />
            Weekly email digest (placeholder)
          </label>
          <label className={styles.checkRow}>
            <input
              type="checkbox"
              checked={prefs.productUpdates}
              onChange={(ev) => setPrefs((p) => ({ ...p, productUpdates: ev.target.checked }))}
            />
            Product update emails (placeholder)
          </label>
          {prefsSaved && (
            <p className={styles.formSuccess} role="status">
              Preferences saved in this browser.
            </p>
          )}
          <Button type="submit">Save preferences</Button>
        </form>
      </section>

      <div className={styles.actions}>
        <Button type="button" variant="danger" onClick={() => void logout()}>
          Log out
        </Button>
      </div>
    </section>
  );
}
