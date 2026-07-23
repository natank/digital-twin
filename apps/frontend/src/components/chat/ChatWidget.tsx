import { useCallback, useEffect, useRef, useState, type JSX } from 'react';

import { createChatSession, getDemoOwnerId, type MessageWire } from '../../lib/api/chat';
import { ChatStreamError, streamChatReply } from '../../lib/api/chatStream';
import { ApiClientError } from '../../lib/api/client';
import { ChatComposer } from './ChatComposer';
import styles from './ChatWidget.module.css';
import { MessageBubble } from './MessageBubble';
import { MessageList } from './MessageList';

export interface ChatWidgetProps {
  /** Override demo owner (defaults to VITE_DEMO_OWNER_ID or ?owner=). */
  ownerId?: string;
}

function localId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function ChatWidget({ ownerId }: ChatWidgetProps): JSX.Element {
  const resolvedOwner = (ownerId || getDemoOwnerId()).trim();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [title, setTitle] = useState('Digital Twin');
  const [messages, setMessages] = useState<MessageWire[]>([]);
  const [draft, setDraft] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [sending, setSending] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const startSession = useCallback(async (): Promise<void> => {
    if (!resolvedOwner) {
      return;
    }
    setStarting(true);
    setError(null);
    try {
      const session = await createChatSession(resolvedOwner);
      setSessionId(session.session_id);
      const name = session.owner_first_name || 'Digital Twin';
      const headline = session.owner_headline;
      setTitle(headline ? `${name} · ${headline}` : `Chat with ${name}`);
    } catch (err) {
      setError(
        err instanceof ApiClientError
          ? err.message
          : 'Could not start chat session. Is the API running?',
      );
    } finally {
      setStarting(false);
    }
  }, [resolvedOwner]);

  useEffect(() => {
    if (resolvedOwner && !sessionId && !starting) {
      void startSession();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional mount/owner start
  }, [resolvedOwner]);

  async function handleSend(): Promise<void> {
    const content = draft.trim();
    if (!content || !sessionId || sending) {
      return;
    }
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;

    setSending(true);
    setError(null);
    setNotice(null);
    setDraft('');
    setStreamingText('');

    const visitorMsg: MessageWire = {
      id: localId('vis'),
      sender: 'visitor',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, visitorMsg]);

    let assembled = '';
    let boundary = false;

    try {
      await streamChatReply(sessionId, content, {
        signal: ac.signal,
        onMeta: (meta) => {
          boundary = meta.boundary_redirect;
        },
        onToken: (chunk) => {
          assembled += chunk;
          setStreamingText(assembled);
        },
      });

      const reply: MessageWire = {
        id: localId('ai'),
        sender: 'ai',
        content: assembled || '(empty reply)',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, reply]);
      setStreamingText('');
      if (boundary) {
        setNotice('That topic is outside this twin’s scope. Try a professional question.');
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }
      setDraft(content);
      // Remove optimistic visitor message on hard failure so retry is clean
      setMessages((prev) => prev.filter((m) => m.id !== visitorMsg.id));
      setStreamingText('');
      const message =
        err instanceof ChatStreamError || err instanceof ApiClientError
          ? err.message
          : 'Failed to stream reply.';
      setError(message);
    } finally {
      setSending(false);
      abortRef.current = null;
    }
  }

  if (!resolvedOwner) {
    return (
      <div className={styles.setup} role="status">
        <p>
          Set <code>VITE_DEMO_OWNER_ID</code> to a seed owner UUID (from the database after{' '}
          <code>pnpm db:seed</code>), or open <code>/chat?owner=&lt;uuid&gt;</code>.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.widget}>
      <div className={styles.header}>
        <h2>{title}</h2>
        <span className={styles.meta}>{sessionId ? 'Session active' : 'Starting…'}</span>
      </div>
      {notice && <p className={styles.notice}>{notice}</p>}
      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}
      <MessageList
        messages={messages}
        scrollKey={sending || streamingText}
        footer={
          sending ? (
            <MessageBubble
              isStreaming
              message={{
                id: 'streaming',
                sender: 'ai',
                content: streamingText || 'Thinking…',
              }}
            />
          ) : null
        }
      />
      <ChatComposer
        value={draft}
        onChange={setDraft}
        onSubmit={() => void handleSend()}
        disabled={!sessionId}
        isLoading={sending}
        placeholder={sessionId ? 'Type a message…' : 'Starting session…'}
      />
    </div>
  );
}
