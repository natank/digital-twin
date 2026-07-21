import { FormEvent, useEffect, useState, type JSX } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Button, Input, isValidEmail } from 'frontend-shared';

import { ApiClientError } from '../lib/api/client';
import { useAuth } from '../lib/auth/AuthContext';
import styles from './Page.module.css';

export function LoginPage(): JSX.Element {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const next = params.get('next') || '/dashboard';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate(next, { replace: true });
    }
  }, [isAuthenticated, navigate, next]);

  async function onSubmit(e: FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    const fe: { email?: string; password?: string } = {};
    if (!isValidEmail(email)) {
      fe.email = 'Enter a valid email address';
    }
    if (!password) {
      fe.password = 'Password is required';
    }
    setFieldErrors(fe);
    if (Object.keys(fe).length > 0) {
      return;
    }

    setSubmitting(true);
    try {
      await login(email.trim(), password);
      navigate(next, { replace: true });
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Login failed. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className={styles.page}>
      <h1>Log in</h1>
      <p className={styles.lead}>Access your Digital Twin dashboard.</p>
      <form className={styles.form} onSubmit={(e) => void onSubmit(e)} noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(ev) => setEmail(ev.target.value)}
          error={fieldErrors.email}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(ev) => setPassword(ev.target.value)}
          error={fieldErrors.password}
        />
        {error && (
          <p className={styles.formError} role="alert">
            {error}
          </p>
        )}
        <Button type="submit" isLoading={submitting}>
          Log in
        </Button>
      </form>
      <p className={styles.formFooter}>
        <Link to="/forgot-password">Forgot password?</Link>
        {' · '}
        No account? <Link to="/register">Register</Link>
      </p>
      <p className={styles.muted}>OAuth (Google / GitHub) coming soon.</p>
    </section>
  );
}
