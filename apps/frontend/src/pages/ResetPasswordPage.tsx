import { FormEvent, useState, type JSX } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button, Input, validatePasswordStrength } from 'frontend-shared';

import { resetPasswordRequest } from '../lib/api/auth';
import { ApiClientError } from '../lib/api/client';
import styles from './Page.module.css';

export function ResetPasswordPage(): JSX.Element {
  const [params] = useSearchParams();
  const token = params.get('token') ?? '';

  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    if (!token) {
      setError('Missing reset token. Open the link from your email.');
      return;
    }
    const problems = validatePasswordStrength(password);
    if (problems.length > 0) {
      setPasswordError(problems[0]);
      return;
    }
    setPasswordError(undefined);
    setSubmitting(true);
    try {
      await resetPasswordRequest(token, password);
      setDone(true);
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Reset failed. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className={styles.page}>
      <h1>Reset password</h1>
      <p className={styles.lead}>Choose a new password for your account.</p>
      {done ? (
        <p className={styles.formSuccess} role="status">
          Password updated. You can <Link to="/login">log in</Link> now.
        </p>
      ) : (
        <form className={styles.form} onSubmit={(e) => void onSubmit(e)} noValidate>
          <Input
            label="New password"
            type="password"
            autoComplete="new-password"
            required
            value={password}
            onChange={(ev) => setPassword(ev.target.value)}
            error={passwordError}
            helperText="Min 8 chars, uppercase, number, and special character."
          />
          {error && (
            <p className={styles.formError} role="alert">
              {error}
            </p>
          )}
          <Button type="submit" isLoading={submitting} disabled={!token}>
            Update password
          </Button>
        </form>
      )}
      <p className={styles.formFooter}>
        <Link to="/login">Back to log in</Link>
      </p>
    </section>
  );
}
