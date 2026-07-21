import type { JSX } from 'react';
import { Link } from 'react-router-dom';

import styles from './Page.module.css';

/** Marketing homepage — expanded in Phase 3 PR-003. */
export function HomePage(): JSX.Element {
  return (
    <section className={styles.page}>
      <h1>Your AI professional presence</h1>
      <p className={styles.lead}>
        Digital Twin hosts a conversational profile visitors can chat with — while you stay focused
        on real work.
      </p>
      <div className={styles.actions}>
        <Link className={styles.primaryLink} to="/chat">
          Try the demo chat
        </Link>
        <Link className={styles.secondaryLink} to="/register">
          Create an account
        </Link>
      </div>
    </section>
  );
}
