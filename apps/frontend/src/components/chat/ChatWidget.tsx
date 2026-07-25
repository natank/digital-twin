import { useCallback, useEffect, useRef, useState, type JSX } from 'react';
import { Button, Input } from 'frontend-shared';

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
  /**
   * Owner-facing preview mode (e.g. dashboard "Public chat" link). Shows the
   * raw resolved owner id ("Previewing as {uuid}") — meaningful for an owner
   * confirming their own twin, but confusing debug text for a real visitor,
   * so it's hidden unless explicitly requested.
   */
  preview?: boolean;
}

type ErrorKind = 'session' | 'send' | null;

/**
 * 'explicit'      — caller passed an owner id (dashboard link, ?owner= in the URL).
 * 'demo-fallback' — no owner id was supplied; VITE_DEMO_OWNER_ID kicked in silently.
 */
type OwnerSource = 'explicit' | 'demo-fallback';

function localId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function ChatWidget({ ownerId, preview = false }: ChatWidgetProps): JSX.Element {
  const propOwner = (ownerId || '').trim();
  const [activeOwner, setActiveOwner] = useState(propOwner);
  const [ownerSource, setOwnerSource] = useState<OwnerSource>(
    propOwner ? 'explicit' : 'demo-fallback',
  );
  const [ownerOverride, setOwnerOverride] = useState('');
  const [switcherOpen, setSwitcherOpen] = useState(false);
  const ownerInputRef = useRef<HTMLInputElement | null>(null);
  const resolvedOwner = (activeOwner || getDemoOwnerId()).trim();
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

  // Move focus into the owner field when the switcher expands.
  useEffect(() => {
    if (switcherOpen) {
      ownerInputRef.current?.focus();
    }
  }, [switcherOpen]);

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

  function handleSwitchOwner(): void {
    const next = ownerOverride.trim();
    if (!next || next === resolvedOwner) {
      return;
    }
    // Reset session/conversation state so the widget starts fresh against the new owner.
    abortRef.current?.abort();
    startedOnce.current = false;
    composerFocusRef.current = false;
    setSessionId(null);
    setMessages([]);
    setDraft('');
    setError(null);
    setErrorKind(null);
    setNotice(null);
    setStreamingText('');
    setLastFailedContent(null);
    setOwnerOverride('');
    setOwnerSource('explicit');
    setActiveOwner(next);
    setSwitcherOpen(false);
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
        <span className={styles.headerMeta}>
          <span id="chat-widget-status" className={styles.meta} aria-live="polite">
            {statusText}
          </span>
          <button
            type="button"
            className={styles.switcherToggle}
            aria-expanded={switcherOpen}
            aria-controls="chat-owner-switcher"
            onClick={() => setSwitcherOpen((open) => !open)}
          >
            {switcherOpen ? 'Cancel' : 'Switch owner'}
          </button>
        </span>
      </header>
      {ownerSource === 'demo-fallback' && (
        <p className={styles.sampleBanner} role="status">
          <strong>Sample twin.</strong> This is a demo profile, not a real owner&apos;s twin.
        </p>
      )}
      {preview && (
        <p className={styles.ownerMeta}>
          Previewing as <code>{resolvedOwner}</code>
        </p>
      )}
      {switcherOpen && (
        <div id="chat-owner-switcher" className={styles.ownerSwitcher}>
          <div className={styles.ownerSwitcherField}>
            <Input
              label="Switch owner"
              placeholder="Paste an owner UUID"
              value={ownerOverride}
              onChange={(e) => setOwnerOverride(e.target.value)}
              ref={ownerInputRef}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleSwitchOwner();
                } else if (e.key === 'Escape') {
                  setSwitcherOpen(false);
                  setOwnerOverride('');
                }
              }}
            />
          </div>
          <Button
            type="button"
            size="small"
            variant="secondary"
            onClick={handleSwitchOwner}
            disabled={!ownerOverride.trim() || ownerOverride.trim() === resolvedOwner}
          >
            Switch
          </Button>
        </div>
      )}
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
