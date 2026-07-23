import { useCallback, useEffect, useState, type JSX } from 'react';

import {
  createChatSession,
  getDemoOwnerId,
  sendChatMessage,
  type MessageWire,
} from '../../lib/api/chat';
import { ApiClientError } from '../../lib/api/client';
import { ChatComposer } from './ChatComposer';
import styles from './ChatWidget.module.css';
import { MessageBubble } from './MessageBubble';
import { MessageList } from './MessageList';

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

  async function handleSend(): Promise<void> {
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
      <MessageList
        messages={messages}
        scrollKey={sending}
        footer={
          sending ? (
            <MessageBubble
              isStreaming
              message={{
                id: 'typing',
                sender: 'ai',
                content: 'Thinking…',
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
