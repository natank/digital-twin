import { useEffect, useRef, type JSX, type ReactNode } from 'react';

import type { MessageWire } from '../../lib/api/chat';
import { scrollBehavior } from './chatA11y';
import { MessageBubble } from './MessageBubble';
import styles from './MessageList.module.css';

export interface MessageListProps {
  messages: MessageWire[];
  emptyHint?: string;
  footer?: ReactNode;
  /** Scroll when messages or footer change. */
  scrollKey?: string | number | boolean;
  /** Accessible name for the message log. */
  ariaLabel?: string;
}

export function MessageList({
  messages,
  emptyHint = 'Ask about experience, skills, or career background.',
  footer,
  scrollKey,
  ariaLabel = 'Conversation messages',
}: MessageListProps): JSX.Element {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = bottomRef.current;
    if (el && typeof el.scrollIntoView === 'function') {
      el.scrollIntoView({ behavior: scrollBehavior() });
    }
  }, [messages, scrollKey, footer]);

  return (
    <div
      className={styles.messages}
      aria-live="polite"
      role="log"
      aria-relevant="additions"
      aria-label={ariaLabel}
      tabIndex={0}
    >
      {messages.length === 0 && !footer && <p className={styles.hint}>{emptyHint}</p>}
      <ol className={styles.list}>
        {messages.map((m) => (
          <li key={m.id} className={styles.item}>
            <MessageBubble message={m} />
          </li>
        ))}
      </ol>
      {footer}
      <div ref={bottomRef} />
    </div>
  );
}
