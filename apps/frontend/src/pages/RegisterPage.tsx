import { FormEvent, useEffect, useState, type JSX } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Input, isValidEmail, validatePasswordStrength } from 'frontend-shared';

import { ApiClientError } from '../lib/api/client';
import { useAuth } from '../lib/auth/AuthContext';
import styles from './Page.module.css';

export function RegisterPage(): JSX.Element {
  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  async function onSubmit(e: FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    const fe: Record<string, string> = {};
    if (!firstName.trim()) {
      fe.firstName = 'First name is required';
    }
    if (!lastName.trim()) {
      fe.lastName = 'Last name is required';
    }
    if (!isValidEmail(email)) {
      fe.email = 'Enter a valid email address';
    }
    const pwProblems = validatePasswordStrength(password);
    if (pwProblems.length > 0) {
      fe.password = pwProblems[0] ?? 'Password is too weak';
    }
    setFieldErrors(fe);
    if (Object.keys(fe).length > 0) {
      return;
    }

    setSubmitting(true);
    try {
      await register({
        email: email.trim(),
        password,
        firstName: firstName.trim(),
        lastName: lastName.trim(),
      });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Registration failed. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className={styles.page}>
      <h1>Create your account</h1>
      <p className={styles.lead}>Register as an owner to host your digital twin.</p>
      <form className={styles.form} onSubmit={(e) => void onSubmit(e)} noValidate>
        <Input
          label="First name"
          autoComplete="given-name"
          required
          value={firstName}
          onChange={(ev) => setFirstName(ev.target.value)}
          error={fieldErrors.firstName}
        />
        <Input
          label="Last name"
          autoComplete="family-name"
          required
          value={lastName}
          onChange={(ev) => setLastName(ev.target.value)}
          error={fieldErrors.lastName}
        />
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
          autoComplete="new-password"
          required
          value={password}
          onChange={(ev) => setPassword(ev.target.value)}
          error={fieldErrors.password}
          helperText="Min 8 chars, uppercase, number, and special character."
        />
        {error && (
          <p className={styles.formError} role="alert">
            {error}
          </p>
        )}
        <Button type="submit" isLoading={submitting}>
          Register
        </Button>
      </form>
      <p className={styles.formFooter}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
      <p className={styles.muted}>Google / GitHub sign-up coming soon.</p>
    </section>
  );
}
