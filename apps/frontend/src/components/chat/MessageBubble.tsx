import type { JSX } from 'react';

import type { MessageWire } from '../../lib/api/chat';
import styles from './MessageBubble.module.css';

export interface MessageBubbleProps {
  message: MessageWire;
  /** When true, renders a live typing/streaming placeholder style. */
  isStreaming?: boolean;
}

function formatTime(iso: string | null | undefined): string | null {
  if (!iso) {
    return null;
  }
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) {
    return null;
  }
  return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
}

export function MessageBubble({ message, isStreaming = false }: MessageBubbleProps): JSX.Element {
  const isVisitor = message.sender === 'visitor';
  const time = formatTime(message.created_at);
  const roleLabel = isVisitor ? 'You' : 'Digital twin';

  return (
    <div
      className={[
        styles.row,
        isVisitor ? styles.rowVisitor : styles.rowAi,
        isStreaming ? styles.streaming : '',
      ]
        .filter(Boolean)
        .join(' ')}
      data-sender={message.sender}
    >
      <div
        className={[styles.bubble, isVisitor ? styles.visitor : styles.ai].join(' ')}
        role="article"
        aria-label={`${roleLabel} message`}
      >
        <p className={styles.content}>{message.content}</p>
        {time && (
          <time className={styles.time} dateTime={message.created_at ?? undefined}>
            {time}
          </time>
        )}
      </div>
    </div>
  );
}
