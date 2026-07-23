/**
 * SSE client for chat replies via POST /chat/sse/{sessionId}/stream.
 *
 * Backend emits:
 *   event: meta  data: {"boundary_redirect": bool}
 *   event: token data: <chunk text>
 *   event: done  data: {"status":"completed"}
 */

import { getApiBaseUrl } from './client';

export interface StreamChatCallbacks {
  onMeta?: (meta: { boundary_redirect: boolean }) => void;
  onToken: (chunk: string) => void;
  onDone?: () => void;
  signal?: AbortSignal;
}

export class ChatStreamError extends Error {
  readonly httpStatus: number | undefined;

  constructor(message: string, httpStatus?: number) {
    super(message);
    this.name = 'ChatStreamError';
    this.httpStatus = httpStatus;
  }
}

/**
 * Stream a chat reply. Visitor message is persisted server-side when the
 * stream starts (same as synchronous post_message).
 */
export async function streamChatReply(
  sessionId: string,
  content: string,
  callbacks: StreamChatCallbacks,
): Promise<void> {
  const url = `${getApiBaseUrl()}/chat/sse/${encodeURIComponent(sessionId)}/stream`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify({ content }),
    signal: callbacks.signal,
  });

  if (!response.ok) {
    let message = response.statusText || 'Stream request failed';
    try {
      const body = (await response.json()) as {
        error?: { message?: string };
      };
      if (body.error?.message) {
        message = body.error.message;
      }
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ChatStreamError(message, response.status);
  }

  if (!response.body) {
    throw new ChatStreamError('No response body for SSE stream');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let eventName = 'message';
  const dataLines: string[] = [];

  const flushEvent = (): void => {
    if (dataLines.length === 0) {
      eventName = 'message';
      return;
    }
    const data = dataLines.join('\n');
    dataLines.length = 0;
    const name = eventName;
    eventName = 'message';

    if (name === 'meta') {
      try {
        const parsed = JSON.parse(data) as { boundary_redirect?: boolean };
        callbacks.onMeta?.({ boundary_redirect: Boolean(parsed.boundary_redirect) });
      } catch {
        // ignore malformed meta
      }
      return;
    }
    if (name === 'token') {
      callbacks.onToken(data);
      return;
    }
    if (name === 'done') {
      callbacks.onDone?.();
    }
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (line === '') {
        flushEvent();
        continue;
      }
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim();
        continue;
      }
      if (line.startsWith('data:')) {
        // SSE allows optional space after colon
        dataLines.push(line.slice(5).replace(/^ /, ''));
      }
    }
  }
  // trailing event without blank line
  flushEvent();
  callbacks.onDone?.();
}
