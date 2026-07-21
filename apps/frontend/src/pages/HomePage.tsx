import type { JSX } from 'react';
import { Link } from 'react-router-dom';

import styles from './Page.module.css';

export function HomePage(): JSX.Element {
  return (
    <section className={styles.page}>
      <h1>Your AI professional presence</h1>
      <p className={styles.lead}>
        Digital Twin hosts a conversational profile visitors can chat with — while you stay focused
        on real work. Upload a CV, tune tone and topics, and get notified when someone engages.
      </p>
      <div className={styles.actions}>
        <Link className={styles.primaryLink} to="/chat">
          Try the demo chat
        </Link>
        <Link className={styles.secondaryLink} to="/register">
          Create an account
        </Link>
      </div>

      <ul className={styles.featureList} aria-label="Product highlights">
        <li>
          <strong>Always-on twin</strong>
          <span>Answer common career questions from your profile summary.</span>
        </li>
        <li>
          <strong>Owner dashboard</strong>
          <span>Manage profile, notifications, and twin configuration.</span>
        </li>
        <li>
          <strong>Pushover alerts</strong>
          <span>Know when a visitor starts a conversation (Phase 2 API).</span>
        </li>
      </ul>

      <p className={styles.muted}>
        New here? Read the <Link to="/about">product overview</Link> or{' '}
        <Link to="/login">log in</Link>.
      </p>
    </section>
  );
}
