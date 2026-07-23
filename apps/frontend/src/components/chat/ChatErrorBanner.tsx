import type { JSX } from 'react';
import { Button } from 'frontend-shared';

import styles from './ChatErrorBanner.module.css';

export interface ChatErrorBannerProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  retryLabel?: string;
}

export function ChatErrorBanner({
  message,
  onRetry,
  onDismiss,
  retryLabel = 'Retry',
}: ChatErrorBannerProps): JSX.Element {
  return (
    <div className={styles.banner} role="alert">
      <p className={styles.message}>{message}</p>
      <div className={styles.actions}>
        {onRetry && (
          <Button type="button" size="small" variant="secondary" onClick={onRetry}>
            {retryLabel}
          </Button>
        )}
        {onDismiss && (
          <Button type="button" size="small" variant="secondary" onClick={onDismiss}>
            Dismiss
          </Button>
        )}
      </div>
    </div>
  );
}
