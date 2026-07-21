import type { JSX } from 'react';
import { Link } from 'react-router-dom';
import { Button } from 'frontend-shared';

import { useAuth } from '../lib/auth/AuthContext';
import styles from './Page.module.css';

export function DashboardPage(): JSX.Element {
  const { owner, logout } = useAuth();
  const name = owner ? `${owner.first_name} ${owner.last_name}`.trim() : 'Owner';

  return (
    <section className={styles.page}>
      <h1>Dashboard</h1>
      <p className={styles.lead}>
        Welcome, {name}. This is your owner home. Profile, notifications, and twin config screens
        arrive in Weeks 12–14.
      </p>
      <p className={styles.muted}>Signed in as {owner?.email}</p>

      <div className={styles.cardGrid}>
        <Link className={styles.card} to="/dashboard">
          <h2>Profile</h2>
          <p>CV upload and summary review (Week 12).</p>
        </Link>
        <Link className={styles.card} to="/chat">
          <h2>Public chat</h2>
          <p>Preview the visitor chat experience.</p>
        </Link>
        <div className={styles.card}>
          <h2>Notifications</h2>
          <p>In-app center and Pushover (Week 14).</p>
        </div>
        <div className={styles.card}>
          <h2>Twin config</h2>
          <p>Prompt, tone, and topics (Week 14).</p>
        </div>
      </div>

      <div className={styles.actions}>
        <Button variant="secondary" type="button" onClick={() => void logout()}>
          Log out
        </Button>
      </div>
    </section>
  );
}
