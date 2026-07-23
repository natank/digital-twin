import { useEffect, useRef, type JSX, type ReactNode } from 'react';

import type { MessageWire } from '../../lib/api/chat';
import { MessageBubble } from './MessageBubble';
import styles from './MessageList.module.css';

export interface MessageListProps {
  messages: MessageWire[];
  emptyHint?: string;
  footer?: ReactNode;
  /** Scroll when messages or footer change. */
  scrollKey?: string | number | boolean;
}

export function MessageList({
  messages,
  emptyHint = 'Ask about experience, skills, or career background.',
  footer,
  scrollKey,
}: MessageListProps): JSX.Element {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = bottomRef.current;
    if (el && typeof el.scrollIntoView === 'function') {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, scrollKey, footer]);

  return (
    <div className={styles.messages} aria-live="polite" role="log" aria-relevant="additions">
      {messages.length === 0 && !footer && <p className={styles.hint}>{emptyHint}</p>}
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
      {footer}
      <div ref={bottomRef} />
    </div>
  );
}
