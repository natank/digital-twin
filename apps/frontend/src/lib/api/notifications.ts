/** Notifications API helpers (`/notifications/me/*`). */

import { apiFetch } from './client';

export interface NotificationWire {
  id: string;
  type: string;
  title: string;
  message: string;
  data: Record<string, unknown> | null;
  priority: number;
  read: boolean;
  delivery_status: string;
  retry_count: number;
  created_at?: string | null;
  sent_at?: string | null;
}

export interface NotificationListWire {
  items: NotificationWire[];
  total: number;
  limit: number;
  offset: number;
  unread_count: number;
}

export interface PushoverConfigWire {
  configured: boolean;
  enabled: boolean;
  device: string | null;
  sound: string | null;
  user_key_masked: string | null;
}

export interface NotificationPreferencesWire {
  global_push_enabled: boolean;
  types: Record<string, boolean>;
}

export function listNotifications(
  token: string,
  opts: { limit?: number; offset?: number; unreadOnly?: boolean } = {},
): Promise<NotificationListWire> {
  const params = new URLSearchParams();
  if (opts.limit != null) params.set('limit', String(opts.limit));
  if (opts.offset != null) params.set('offset', String(opts.offset));
  if (opts.unreadOnly) params.set('unread_only', 'true');
  const qs = params.toString();
  return apiFetch<NotificationListWire>(`/notifications/me${qs ? `?${qs}` : ''}`, { token });
}

export function getUnreadCount(token: string): Promise<{ unread_count: number }> {
  return apiFetch<{ unread_count: number }>('/notifications/me/unread-count', { token });
}

export function markNotificationRead(token: string, id: string): Promise<NotificationWire> {
  return apiFetch<NotificationWire>(`/notifications/me/${id}/read`, {
    method: 'POST',
    token,
  });
}

export function markAllNotificationsRead(token: string): Promise<{ marked_read: number }> {
  return apiFetch<{ marked_read: number }>('/notifications/me/read-all', {
    method: 'POST',
    token,
  });
}

export function deleteNotification(
  token: string,
  id: string,
): Promise<{ message?: string } | null> {
  return apiFetch(`/notifications/me/${id}`, { method: 'DELETE', token });
}

export function getPushoverConfig(token: string): Promise<PushoverConfigWire> {
  return apiFetch<PushoverConfigWire>('/notifications/me/pushover', { token });
}

export function updatePushoverConfig(
  token: string,
  body: { user_key: string; device?: string | null; sound?: string; enabled?: boolean },
): Promise<PushoverConfigWire> {
  return apiFetch<PushoverConfigWire>('/notifications/me/pushover', {
    method: 'PUT',
    token,
    body: JSON.stringify(body),
  });
}

export function deletePushoverConfig(token: string): Promise<{ message?: string } | null> {
  return apiFetch('/notifications/me/pushover', { method: 'DELETE', token });
}

export function getNotificationPreferences(token: string): Promise<NotificationPreferencesWire> {
  return apiFetch<NotificationPreferencesWire>('/notifications/me/preferences', { token });
}

export function updateNotificationPreferences(
  token: string,
  body: { global_push_enabled?: boolean; types?: Record<string, boolean> },
): Promise<NotificationPreferencesWire> {
  return apiFetch<NotificationPreferencesWire>('/notifications/me/preferences', {
    method: 'PUT',
    token,
    body: JSON.stringify(body),
  });
}

export function sendTestNotification(
  token: string,
): Promise<{ notification_id: string; delivery_status: string; message: string }> {
  return apiFetch('/notifications/me/test', { method: 'POST', token });
}
