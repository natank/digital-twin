import { useCallback, useEffect, useState, type JSX } from 'react';

import { getUnreadCount } from '../../lib/api/notifications';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from './UnreadBadge.module.css';

/** Small count badge for dashboard nav; polls periodically. */
export function UnreadBadge(): JSX.Element | null {
  const { token, isAuthenticated } = useAuth();
  const [count, setCount] = useState(0);

  const refresh = useCallback(async (): Promise<void> => {
    if (!token) {
      setCount(0);
      return;
    }
    try {
      const data = await getUnreadCount(token);
      setCount(data.unread_count);
    } catch {
      // Keep last known count on transient errors.
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated) {
      setCount(0);
      return;
    }
    void refresh();
    const id = window.setInterval(() => void refresh(), 30_000);
    return () => window.clearInterval(id);
  }, [isAuthenticated, refresh]);

  if (count <= 0) {
    return null;
  }

  return (
    <span className={styles.badge} aria-label={`${count} unread notifications`}>
      {count > 99 ? '99+' : count}
    </span>
  );
}
