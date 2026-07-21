import type { JSX } from 'react';
import { Link } from 'react-router-dom';

import styles from './Page.module.css';

export function AboutPage(): JSX.Element {
  return (
    <section className={styles.page}>
      <h1>About Digital Twin</h1>
      <p className={styles.lead}>
        Digital Twin turns your professional profile into an always-on conversational assistant.
        Owners upload a CV, tune tone and topics, and receive notifications when visitors engage.
      </p>
      <h2 className={styles.subheading}>How it works</h2>
      <ol className={styles.steps}>
        <li>Register and verify your owner account.</li>
        <li>Upload a CV; we extract text and generate a profile summary.</li>
        <li>Customize system prompt, tone, and topic boundaries.</li>
        <li>Share the public chat experience with visitors.</li>
        <li>Review conversations and notifications from your dashboard.</li>
      </ol>
      <p>
        The backend (Phases 1–2) already provides Auth, Profile, Chat, Notifications, and Config
        APIs. This SPA is the product surface for those services.
      </p>
      <div className={styles.actions}>
        <Link className={styles.primaryLink} to="/register">
          Get started
        </Link>
        <Link className={styles.secondaryLink} to="/chat">
          Open demo chat
        </Link>
      </div>
    </section>
  );
}
