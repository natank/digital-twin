import { useCallback, useEffect, useRef, useState, type JSX } from 'react';

import { createChatSession, getDemoOwnerId, type MessageWire } from '../../lib/api/chat';
import { ChatStreamError, streamChatReply } from '../../lib/api/chatStream';
import { ApiClientError } from '../../lib/api/client';
import { ChatComposer } from './ChatComposer';
import { ChatErrorBanner } from './ChatErrorBanner';
import styles from './ChatWidget.module.css';
import { MessageList } from './MessageList';
import { TypingIndicator } from './TypingIndicator';

export interface ChatWidgetProps {
  /** Override demo owner (defaults to VITE_DEMO_OWNER_ID or ?owner=). */
  ownerId?: string;
}

type ErrorKind = 'session' | 'send' | null;

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
  const [errorKind, setErrorKind] = useState<ErrorKind>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [sending, setSending] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [lastFailedContent, setLastFailedContent] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const startedOnce = useRef(false);
  const composerFocusRef = useRef(false);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  // Move focus into the composer once a session is ready (one-shot).
  useEffect(() => {
    if (sessionId && !composerFocusRef.current) {
      composerFocusRef.current = true;
      const el = document.getElementById('chat-composer-input');
      if (el && typeof el.focus === 'function') {
        el.focus();
      }
    }
  }, [sessionId]);

  const startSession = useCallback(async (): Promise<void> => {
    if (!resolvedOwner) {
      return;
    }
    setStarting(true);
    setError(null);
    setErrorKind(null);
    try {
      const session = await createChatSession(resolvedOwner);
      setSessionId(session.session_id);
      const name = session.owner_first_name || 'Digital Twin';
      const headline = session.owner_headline;
      setTitle(headline ? `${name} · ${headline}` : `Chat with ${name}`);
      startedOnce.current = true;
    } catch (err) {
      setErrorKind('session');
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
    if (resolvedOwner && !sessionId && !starting && !startedOnce.current) {
      void startSession();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional mount/owner start
  }, [resolvedOwner]);

  const sendContent = useCallback(
    async (content: string): Promise<void> => {
      if (!content || !sessionId || sending) {
        return;
      }
      abortRef.current?.abort();
      const ac = new AbortController();
      abortRef.current = ac;

      setSending(true);
      setError(null);
      setErrorKind(null);
      setNotice(null);
      setStreamingText('');
      setLastFailedContent(null);

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
        setLastFailedContent(content);
        setMessages((prev) => prev.filter((m) => m.id !== visitorMsg.id));
        setStreamingText('');
        setErrorKind('send');
        const message =
          err instanceof ChatStreamError || err instanceof ApiClientError
            ? err.message
            : 'Failed to stream reply.';
        setError(message);
      } finally {
        setSending(false);
        abortRef.current = null;
      }
    },
    [sessionId, sending],
  );

  async function handleSend(): Promise<void> {
    const content = draft.trim();
    if (!content) {
      return;
    }
    setDraft('');
    await sendContent(content);
  }

  function handleRetry(): void {
    if (errorKind === 'session') {
      startedOnce.current = false;
      void startSession();
      return;
    }
    if (errorKind === 'send' && lastFailedContent) {
      setDraft('');
      void sendContent(lastFailedContent);
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

  const statusText = starting ? 'Connecting…' : sessionId ? 'Session active' : 'Not connected';

  return (
    <section
      className={styles.widget}
      aria-labelledby="chat-widget-title"
      aria-describedby="chat-widget-status"
    >
      <header className={styles.header}>
        <h2 id="chat-widget-title">{title}</h2>
        <span id="chat-widget-status" className={styles.meta} aria-live="polite">
          {statusText}
        </span>
      </header>
      {notice && (
        <p className={styles.notice} role="status">
          {notice}
        </p>
      )}
      {error && (
        <ChatErrorBanner
          message={error}
          onRetry={
            errorKind === 'session' || (errorKind === 'send' && lastFailedContent)
              ? handleRetry
              : undefined
          }
          retryLabel={errorKind === 'session' ? 'Retry connection' : 'Retry send'}
          onDismiss={() => {
            setError(null);
            setErrorKind(null);
          }}
        />
      )}
      <MessageList
        messages={messages}
        scrollKey={sending || streamingText}
        footer={sending ? <TypingIndicator preview={streamingText} /> : null}
      />
      <ChatComposer
        value={draft}
        onChange={setDraft}
        onSubmit={() => void handleSend()}
        disabled={!sessionId || starting}
        isLoading={sending}
        placeholder={
          starting ? 'Connecting…' : sessionId ? 'Type a message…' : 'Reconnect to start chatting…'
        }
      />
    </section>
  );
}
