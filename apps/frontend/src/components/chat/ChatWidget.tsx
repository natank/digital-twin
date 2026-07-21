import { FormEvent, useCallback, useEffect, useRef, useState, type JSX } from 'react';
import { Button } from 'frontend-shared';

import {
  createChatSession,
  getDemoOwnerId,
  sendChatMessage,
  type MessageWire,
} from '../../lib/api/chat';
import { ApiClientError } from '../../lib/api/client';
import styles from './ChatWidget.module.css';

export interface ChatWidgetProps {
  /** Override demo owner (defaults to VITE_DEMO_OWNER_ID or ?owner=). */
  ownerId?: string;
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
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = bottomRef.current;
    if (el && typeof el.scrollIntoView === 'function') {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, sending]);

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
    // Only auto-start once when owner is available.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional mount/owner start
  }, [resolvedOwner]);

  async function onSend(e: FormEvent): Promise<void> {
    e.preventDefault();
    const content = draft.trim();
    if (!content || !sessionId || sending) {
      return;
    }
    setSending(true);
    setError(null);
    setNotice(null);
    setDraft('');
    try {
      const result = await sendChatMessage(sessionId, content);
      setMessages((prev) => [...prev, result.visitor_message, result.reply]);
      if (result.boundary_redirect) {
        setNotice('That topic is outside this twin’s scope. Try a professional question.');
      }
    } catch (err) {
      setDraft(content);
      setError(err instanceof ApiClientError ? err.message : 'Failed to send message.');
    } finally {
      setSending(false);
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
      <div className={styles.messages} aria-live="polite">
        {messages.length === 0 && !sending && (
          <p className={styles.meta}>Ask about experience, skills, or career background.</p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`${styles.bubble} ${m.sender === 'visitor' ? styles.visitor : styles.ai}`}
          >
            {m.content}
          </div>
        ))}
        {sending && <div className={`${styles.bubble} ${styles.ai}`}>Thinking…</div>}
        <div ref={bottomRef} />
      </div>
      <form className={styles.composer} onSubmit={(e) => void onSend(e)}>
        <textarea
          aria-label="Message"
          placeholder={sessionId ? 'Type a message…' : 'Starting session…'}
          value={draft}
          disabled={!sessionId || sending}
          onChange={(ev) => setDraft(ev.target.value)}
          rows={2}
        />
        <Button type="submit" isLoading={sending} disabled={!sessionId || !draft.trim()}>
          Send
        </Button>
      </form>
    </div>
  );
}
