import type { JSX } from 'react';
import { Link } from 'react-router-dom';

import { useAuth } from '../lib/auth/AuthContext';
import styles from './Page.module.css';

export function DashboardPage(): JSX.Element {
  const { owner } = useAuth();
  const name = owner ? `${owner.first_name} ${owner.last_name}`.trim() : 'Owner';

  return (
    <section className={styles.page}>
      <h1>Overview</h1>
      <p className={styles.lead}>
        Welcome, {name}. Manage your professional twin from the sidebar.
      </p>
      <p className={styles.muted}>Signed in as {owner?.email}</p>

      <div className={styles.cardGrid}>
        <Link className={styles.card} to="/dashboard/profile">
          <h2>Profile</h2>
          <p>Edit headline, bio, skills, and upload a CV.</p>
        </Link>
        <Link className={styles.card} to="/dashboard/settings">
          <h2>Settings</h2>
          <p>Account details and password options.</p>
        </Link>
        <Link className={styles.card} to="/chat">
          <h2>Public chat</h2>
          <p>Preview the visitor chat experience.</p>
        </Link>
        <div className={styles.card}>
          <h2>Notifications</h2>
          <p>In-app center and Pushover (Week 14).</p>
        </div>
      </div>
    </section>
  );
}
