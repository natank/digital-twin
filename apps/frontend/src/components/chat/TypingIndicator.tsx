import type { JSX } from 'react';

import styles from './TypingIndicator.module.css';

export interface TypingIndicatorProps {
  /** Optional preview of the streamed text so far. */
  preview?: string;
  label?: string;
}

export function TypingIndicator({
  preview,
  label = 'Digital twin is typing',
}: TypingIndicatorProps): JSX.Element {
  const showPreview = Boolean(preview && preview.trim().length > 0);

  return (
    <div
      className={styles.wrap}
      role="status"
      aria-live="polite"
      aria-label={label}
      data-testid="typing-indicator"
    >
      {showPreview ? (
        <p className={styles.preview}>{preview}</p>
      ) : (
        <div className={styles.dots} aria-hidden>
          <span />
          <span />
          <span />
        </div>
      )}
      {!showPreview && <span className={styles.srOnly}>{label}</span>}
    </div>
  );
}
