/**
 * Shared unread-notification count for the dashboard.
 *
 * `UnreadBadge` (sidebar) and `NotificationsPage` each need the current
 * unread count, but previously kept independent local state — marking a
 * notification read on the page updated the page's own count instantly while
 * the sidebar badge kept showing the stale value until its own 30s poll
 * happened to fire (finding-6). Lifting the count here means both stay in
 * sync the moment a read/delete action completes.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type JSX,
  type ReactNode,
} from 'react';

import { getUnreadCount } from '../api/notifications';
import { useAuth } from '../auth/AuthContext';

export interface NotificationsContextValue {
  unreadCount: number;
  refresh: () => Promise<void>;
}

const NotificationsContext = createContext<NotificationsContextValue | null>(null);

const POLL_INTERVAL_MS = 30_000;

export function NotificationsProvider({ children }: { children: ReactNode }): JSX.Element {
  const { token, isAuthenticated } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  const refresh = useCallback(async (): Promise<void> => {
    if (!token) {
      setUnreadCount(0);
      return;
    }
    try {
      const data = await getUnreadCount(token);
      setUnreadCount(data.unread_count);
    } catch {
      // Keep last known count on transient errors.
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated) {
      setUnreadCount(0);
      return;
    }
    void refresh();
    const id = window.setInterval(() => void refresh(), POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [isAuthenticated, refresh]);

  const value = useMemo<NotificationsContextValue>(
    () => ({ unreadCount, refresh }),
    [unreadCount, refresh],
  );

  return <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>;
}

// Hook co-located with provider (react-refresh only cares about component exports).
// eslint-disable-next-line react-refresh/only-export-components -- useNotificationsContext is the public API
export function useNotificationsContext(): NotificationsContextValue {
  const ctx = useContext(NotificationsContext);
  if (!ctx) {
    throw new Error('useNotificationsContext must be used within NotificationsProvider');
  }
  return ctx;
}
