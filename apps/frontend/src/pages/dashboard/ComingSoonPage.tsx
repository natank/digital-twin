import type { JSX } from 'react';

import styles from '../Page.module.css';

/** Placeholder for dashboard sub-pages until their feature PR lands. */
export function ComingSoonPage({ title, blurb }: { title: string; blurb: string }): JSX.Element {
  return (
    <section className={styles.page}>
      <h1>{title}</h1>
      <p className={styles.lead}>{blurb}</p>
      <p className={styles.muted}>This section is scaffolding for Phase 3 Week 12.</p>
    </section>
  );
}
