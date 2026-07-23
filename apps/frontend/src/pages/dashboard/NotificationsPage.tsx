import { useCallback, useEffect, useState, type JSX } from 'react';
import { Link } from 'react-router-dom';
import { Button } from 'frontend-shared';

import { ApiClientError } from '../../lib/api/client';
import {
  deleteNotification,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type NotificationWire,
} from '../../lib/api/notifications';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from '../Page.module.css';
import notifStyles from './NotificationsPage.module.css';

function formatWhen(iso: string | null | undefined): string {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function NotificationsPage(): JSX.Element {
  const { token } = useAuth();
  const [items, setItems] = useState<NotificationWire[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await listNotifications(token, { limit: 50, unreadOnly });
      setItems(data.items);
      setUnread(data.unread_count);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  }, [token, unreadOnly]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onMarkRead(id: string): Promise<void> {
    if (!token) return;
    setBusyId(id);
    try {
      await markNotificationRead(token, id);
      await load();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to mark read.');
    } finally {
      setBusyId(null);
    }
  }

  async function onMarkAll(): Promise<void> {
    if (!token) return;
    setBusyId('all');
    try {
      await markAllNotificationsRead(token);
      await load();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to mark all read.');
    } finally {
      setBusyId(null);
    }
  }

  async function onDelete(id: string): Promise<void> {
    if (!token) return;
    setBusyId(id);
    try {
      await deleteNotification(token, id);
      await load();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to delete.');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className={styles.page}>
      <header className={notifStyles.header}>
        <div>
          <h1>Notifications</h1>
          <p className={styles.lead}>
            In-app alerts for chat activity and profile jobs.
            {unread > 0 ? ` ${unread} unread.` : ' All caught up.'}
          </p>
        </div>
        <div className={styles.actions}>
          <Button
            type="button"
            variant="secondary"
            size="small"
            onClick={() => setUnreadOnly((v) => !v)}
          >
            {unreadOnly ? 'Show all' : 'Unread only'}
          </Button>
          <Button
            type="button"
            size="small"
            disabled={unread === 0 || busyId === 'all'}
            isLoading={busyId === 'all'}
            onClick={() => void onMarkAll()}
          >
            Mark all read
          </Button>
          <Link className={styles.secondaryLink} to="/dashboard/notifications/pushover">
            Pushover setup
          </Link>
        </div>
      </header>

      {error && (
        <p className={styles.formError} role="alert">
          {error}
        </p>
      )}

      {loading ? (
        <p className={styles.muted} role="status">
          Loading…
        </p>
      ) : items.length === 0 ? (
        <p className={styles.muted}>No notifications yet. Visitors chatting will show up here.</p>
      ) : (
        <ul className={notifStyles.list}>
          {items.map((n) => (
            <li
              key={n.id}
              className={[notifStyles.item, n.read ? '' : notifStyles.unread]
                .filter(Boolean)
                .join(' ')}
            >
              <div className={notifStyles.itemMain}>
                <div className={notifStyles.itemTop}>
                  <strong>{n.title}</strong>
                  <span className={notifStyles.meta}>
                    {n.type.replace(/_/g, ' ')} · {formatWhen(n.created_at)}
                  </span>
                </div>
                <p className={notifStyles.body}>{n.message}</p>
                <p className={notifStyles.meta}>
                  Delivery: {n.delivery_status}
                  {n.priority > 0 ? ` · priority ${n.priority}` : ''}
                </p>
              </div>
              <div className={notifStyles.itemActions}>
                {!n.read && (
                  <Button
                    type="button"
                    size="small"
                    variant="secondary"
                    isLoading={busyId === n.id}
                    onClick={() => void onMarkRead(n.id)}
                  >
                    Mark read
                  </Button>
                )}
                <Button
                  type="button"
                  size="small"
                  variant="danger"
                  disabled={busyId === n.id}
                  onClick={() => void onDelete(n.id)}
                >
                  Delete
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
