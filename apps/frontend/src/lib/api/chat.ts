/** Public chat API helpers (no auth required). */

import { apiFetch } from './client';

export interface ChatSessionWire {
  session_id: string;
  owner_id: string;
  expires_at: string;
  created_at?: string | null;
  owner_headline?: string | null;
  owner_first_name?: string | null;
  flagged?: boolean;
}

export interface MessageWire {
  id: string;
  sender: string;
  content: string;
  tokens_used?: number | null;
  created_at?: string | null;
}

export interface SendMessageResultWire {
  visitor_message: MessageWire;
  reply: MessageWire;
  session_id: string;
  expires_at: string;
  boundary_redirect: boolean;
}

export function createChatSession(ownerId: string): Promise<ChatSessionWire> {
  return apiFetch<ChatSessionWire>('/chat/sessions', {
    method: 'POST',
    body: JSON.stringify({ owner_id: ownerId }),
  });
}

export function sendChatMessage(
  sessionId: string,
  content: string,
): Promise<SendMessageResultWire> {
  return apiFetch<SendMessageResultWire>(`/chat/sessions/${sessionId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export function getDemoOwnerId(): string {
  return (import.meta.env.VITE_DEMO_OWNER_ID || '').trim();
}
