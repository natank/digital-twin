/** Owner conversation browser API (`/chat/me/conversations`). */

import { apiFetch } from './client';
import type { MessageWire } from './chat';

export interface ConversationSummaryWire {
  session_id: string;
  created_at?: string | null;
  expires_at?: string | null;
  flagged: boolean;
  flag_reason?: string | null;
  message_count: number;
  preview?: string | null;
  last_message_at?: string | null;
}

export interface ConversationListWire {
  items: ConversationSummaryWire[];
  total: number;
  limit: number;
  offset: number;
}

export interface ConversationDetailWire {
  session_id: string;
  created_at?: string | null;
  expires_at?: string | null;
  flagged: boolean;
  flag_reason?: string | null;
  messages: MessageWire[];
}

export function listConversations(
  token: string,
  opts: { limit?: number; offset?: number } = {},
): Promise<ConversationListWire> {
  const params = new URLSearchParams();
  if (opts.limit != null) params.set('limit', String(opts.limit));
  if (opts.offset != null) params.set('offset', String(opts.offset));
  const qs = params.toString();
  return apiFetch<ConversationListWire>(`/chat/me/conversations${qs ? `?${qs}` : ''}`, {
    token,
  });
}

export function getConversation(token: string, sessionId: string): Promise<ConversationDetailWire> {
  return apiFetch<ConversationDetailWire>(
    `/chat/me/conversations/${encodeURIComponent(sessionId)}`,
    { token },
  );
}

export function flagConversation(
  token: string,
  sessionId: string,
  body: { flagged: boolean; reason?: string | null },
): Promise<ConversationSummaryWire> {
  return apiFetch<ConversationSummaryWire>(
    `/chat/me/conversations/${encodeURIComponent(sessionId)}/flag`,
    {
      method: 'POST',
      token,
      body: JSON.stringify(body),
    },
  );
}
