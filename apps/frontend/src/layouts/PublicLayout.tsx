import type { JSX } from 'react';
import { Link, Outlet } from 'react-router-dom';

import { useAuth } from '../lib/auth/AuthContext';
import styles from './PublicLayout.module.css';

export function PublicLayout(): JSX.Element {
  const { isAuthenticated, owner, logout } = useAuth();

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Link to="/" className={styles.brand}>
          Digital Twin
        </Link>
        <nav className={styles.nav} aria-label="Main">
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
          <Link to="/chat">Chat</Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <span className={styles.userHint}>{owner?.email}</span>
              <button type="button" className={styles.linkButton} onClick={() => void logout()}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link to="/register" className={styles.cta}>
                Register
              </Link>
            </>
          )}
        </nav>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
      <footer className={styles.footer}>
        <span>Digital Twin · MVP</span>
        <Link to="/about">About</Link>
      </footer>
    </div>
  );
}
