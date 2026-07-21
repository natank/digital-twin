import type { JSX } from 'react';

import styles from './Page.module.css';

/** Temporary route body until the feature PR lands. */
export function PlaceholderPage({ title }: { title: string }): JSX.Element {
  return (
    <section className={styles.page}>
      <h1>{title}</h1>
      <p className={styles.lead}>
        This page is scaffolding for Phase 3. Content lands in a follow-up PR.
      </p>
    </section>
  );
}
