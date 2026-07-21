import { useEffect, useState, type JSX } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { verifyEmailRequest } from '../lib/api/auth';
import { ApiClientError } from '../lib/api/client';
import styles from './Page.module.css';

export function VerifyEmailPage(): JSX.Element {
  const [params] = useSearchParams();
  const token = params.get('token') ?? '';
  const [status, setStatus] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('Missing verification token.');
      return;
    }
    let cancelled = false;
    setStatus('loading');
    void (async () => {
      try {
        await verifyEmailRequest(token);
        if (!cancelled) {
          setStatus('ok');
          setMessage('Email verified. You can log in.');
        }
      } catch (err) {
        if (!cancelled) {
          setStatus('error');
          setMessage(
            err instanceof ApiClientError ? err.message : 'Verification failed. Try again later.',
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <section className={styles.page}>
      <h1>Verify email</h1>
      {status === 'loading' && <p className={styles.muted}>Verifying…</p>}
      {status === 'ok' && (
        <p className={styles.formSuccess} role="status">
          {message}
        </p>
      )}
      {status === 'error' && (
        <p className={styles.formError} role="alert">
          {message}
        </p>
      )}
      <p className={styles.formFooter}>
        <Link to="/login">Go to log in</Link>
      </p>
    </section>
  );
}
