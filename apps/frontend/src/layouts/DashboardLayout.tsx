import { useState, type JSX } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';

import { UnreadBadge } from '../components/notifications/UnreadBadge';
import { useAuth } from '../lib/auth/AuthContext';
import styles from './DashboardLayout.module.css';

const NAV = [
  { to: '/dashboard', end: true, label: 'Overview', badge: false },
  { to: '/dashboard/profile', end: false, label: 'Profile', badge: false },
  { to: '/dashboard/conversations', end: false, label: 'Conversations', badge: false },
  { to: '/dashboard/notifications', end: false, label: 'Notifications', badge: true },
  { to: '/dashboard/settings', end: false, label: 'Settings', badge: false },
] as const;

export function DashboardLayout(): JSX.Element {
  const { owner, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const displayName = owner
    ? `${owner.first_name} ${owner.last_name}`.trim() || owner.email
    : 'Owner';

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar} aria-label="Dashboard">
        <Link to="/dashboard" className={styles.brand}>
          Digital Twin
        </Link>
        <nav className={styles.nav}>
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                [styles.navLink, isActive ? styles.navLinkActive : ''].filter(Boolean).join(' ')
              }
            >
              {item.label}
              {item.badge ? <UnreadBadge /> : null}
            </NavLink>
          ))}
        </nav>
        <div className={styles.sidebarFooter}>
          <Link to="/chat" className={styles.sideMuted}>
            Public chat
          </Link>
          <Link to="/" className={styles.sideMuted}>
            Marketing site
          </Link>
        </div>
      </aside>

      <div className={styles.mainCol}>
        <header className={styles.topbar}>
          <p className={styles.breadcrumb}>Owner dashboard</p>
          <div className={styles.userMenu}>
            <button
              type="button"
              className={styles.userButton}
              aria-expanded={menuOpen}
              aria-haspopup="menu"
              onClick={() => setMenuOpen((v) => !v)}
            >
              <span className={styles.userName}>{displayName}</span>
              <span className={styles.chevron} aria-hidden>
                ▾
              </span>
            </button>
            {menuOpen && (
              <div className={styles.menu} role="menu">
                <p className={styles.menuEmail}>{owner?.email}</p>
                <Link
                  role="menuitem"
                  to="/dashboard/settings"
                  className={styles.menuItem}
                  onClick={() => setMenuOpen(false)}
                >
                  Account settings
                </Link>
                <Link
                  role="menuitem"
                  to="/dashboard/profile"
                  className={styles.menuItem}
                  onClick={() => setMenuOpen(false)}
                >
                  Profile
                </Link>
                <button
                  type="button"
                  role="menuitem"
                  className={styles.menuItem}
                  onClick={() => {
                    setMenuOpen(false);
                    void logout();
                  }}
                >
                  Log out
                </button>
              </div>
            )}
          </div>
        </header>
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
