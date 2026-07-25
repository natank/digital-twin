import type { JSX } from 'react';

import { useNotificationsContext } from '../../lib/notifications/NotificationsContext';
import styles from './UnreadBadge.module.css';

/** Small count badge for dashboard nav; stays in sync via NotificationsContext. */
export function UnreadBadge(): JSX.Element | null {
  const { unreadCount } = useNotificationsContext();

  if (unreadCount <= 0) {
    return null;
  }

  return (
    <span className={styles.badge} aria-label={`${unreadCount} unread notifications`}>
      {unreadCount > 99 ? '99+' : unreadCount}
    </span>
  );
}
