import { useCallback, useEffect, useState, type JSX } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Button } from 'frontend-shared';

import type { MessageWire } from '../../lib/api/chat';
import { ApiClientError } from '../../lib/api/client';
import {
  flagConversation,
  getConversation,
  listConversations,
  type ConversationSummaryWire,
} from '../../lib/api/conversations';
import { useAuth } from '../../lib/auth/AuthContext';
import styles from '../Page.module.css';
import convStyles from './ConversationsPage.module.css';

function formatWhen(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function ConversationsPage(): JSX.Element {
  const { token } = useAuth();
  const { sessionId } = useParams<{ sessionId?: string }>();
  const [items, setItems] = useState<ConversationSummaryWire[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageWire[]>([]);
  const [detailFlagged, setDetailFlagged] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const loadList = useCallback(async (): Promise<void> => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await listConversations(token, { limit: 50 });
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load conversations.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const loadDetail = useCallback(async (): Promise<void> => {
    if (!token || !sessionId) {
      setMessages([]);
      return;
    }
    setDetailLoading(true);
    setError(null);
    try {
      const data = await getConversation(token, sessionId);
      setMessages(data.messages);
      setDetailFlagged(data.flagged);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to load conversation.');
    } finally {
      setDetailLoading(false);
    }
  }, [token, sessionId]);

  useEffect(() => {
    void loadList();
  }, [loadList]);

  useEffect(() => {
    void loadDetail();
  }, [loadDetail]);

  async function onToggleFlag(): Promise<void> {
    if (!token || !sessionId) return;
    try {
      const updated = await flagConversation(token, sessionId, {
        flagged: !detailFlagged,
        reason: detailFlagged ? null : 'Flagged from dashboard',
      });
      setDetailFlagged(updated.flagged);
      await loadList();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Failed to update flag.');
    }
  }

  return (
    <section className={styles.page}>
      <h1>Conversations</h1>
      <p className={styles.lead}>Browse visitor chats with your digital twin ({total} total).</p>
      {error && (
        <p className={styles.formError} role="alert">
          {error}
        </p>
      )}

      <div className={convStyles.layout}>
        <div className={convStyles.listPane}>
          {loading ? (
            <p className={styles.muted}>Loading…</p>
          ) : items.length === 0 ? (
            <p className={styles.muted}>No conversations yet.</p>
          ) : (
            <ul className={convStyles.list}>
              {items.map((item) => (
                <li key={item.session_id}>
                  <Link
                    to={`/dashboard/conversations/${item.session_id}`}
                    className={[
                      convStyles.row,
                      sessionId === item.session_id ? convStyles.rowActive : '',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                  >
                    <span className={convStyles.rowTop}>
                      <time>{formatWhen(item.last_message_at ?? item.created_at)}</time>
                      {item.flagged && <span className={convStyles.flag}>Flagged</span>}
                    </span>
                    <span className={convStyles.preview}>{item.preview || '(no messages)'}</span>
                    <span className={styles.muted}>{item.message_count} messages</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={convStyles.detailPane}>
          {!sessionId ? (
            <p className={styles.muted}>Select a conversation to view the transcript.</p>
          ) : detailLoading ? (
            <p className={styles.muted}>Loading transcript…</p>
          ) : (
            <>
              <div className={convStyles.detailHeader}>
                <h2>Session {sessionId.slice(0, 10)}…</h2>
                <Button
                  type="button"
                  size="small"
                  variant="secondary"
                  onClick={() => void onToggleFlag()}
                >
                  {detailFlagged ? 'Unflag' : 'Flag'}
                </Button>
              </div>
              <ol className={convStyles.transcript}>
                {messages.map((m) => (
                  <li
                    key={m.id}
                    className={m.sender === 'visitor' ? convStyles.msgVisitor : convStyles.msgAi}
                  >
                    <strong>{m.sender === 'visitor' ? 'Visitor' : 'Twin'}</strong>
                    <p>{m.content}</p>
                    <time>{formatWhen(m.created_at)}</time>
                  </li>
                ))}
              </ol>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
