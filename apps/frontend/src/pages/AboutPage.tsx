import type { JSX } from 'react';

import styles from './Page.module.css';

export function AboutPage(): JSX.Element {
  return (
    <section className={styles.page}>
      <h1>About Digital Twin</h1>
      <p className={styles.lead}>
        Digital Twin turns your professional profile into an always-on conversational assistant.
        Owners upload a CV, tune tone and topics, and receive notifications when visitors engage.
      </p>
      <p>
        This MVP is API-backed (auth, profile, chat, notifications, config). The React SPA in Phase
        3 is the product surface for those services.
      </p>
    </section>
  );
}
