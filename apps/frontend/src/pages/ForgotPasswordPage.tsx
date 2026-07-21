import { FormEvent, useState, type JSX } from 'react';
import { Link } from 'react-router-dom';
import { Button, Input, isValidEmail } from 'frontend-shared';

import { forgotPasswordRequest } from '../lib/api/auth';
import { ApiClientError } from '../lib/api/client';
import styles from './Page.module.css';

export function ForgotPasswordPage(): JSX.Element {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | undefined>();
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    if (!isValidEmail(email)) {
      setEmailError('Enter a valid email address');
      return;
    }
    setEmailError(undefined);
    setSubmitting(true);
    try {
      await forgotPasswordRequest(email.trim());
      setDone(true);
    } catch (err) {
      // Backend always succeeds for unknown emails; still handle transport errors.
      const message =
        err instanceof ApiClientError ? err.message : 'Request failed. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className={styles.page}>
      <h1>Forgot password</h1>
      <p className={styles.lead}>
        Enter your account email. If it exists, we will send reset instructions.
      </p>
      {done ? (
        <p className={styles.formSuccess} role="status">
          If an account exists for that email, a reset link has been sent (check server logs in
          local dev).
        </p>
      ) : (
        <form className={styles.form} onSubmit={(e) => void onSubmit(e)} noValidate>
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
            error={emailError}
          />
          {error && (
            <p className={styles.formError} role="alert">
              {error}
            </p>
          )}
          <Button type="submit" isLoading={submitting}>
            Send reset link
          </Button>
        </form>
      )}
      <p className={styles.formFooter}>
        <Link to="/login">Back to log in</Link>
      </p>
    </section>
  );
}
