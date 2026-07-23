import { FormEvent, KeyboardEvent, type JSX } from 'react';
import { Button } from 'frontend-shared';

import styles from './ChatComposer.module.css';

export interface ChatComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatComposer({
  value,
  onChange,
  onSubmit,
  disabled = false,
  isLoading = false,
  placeholder = 'Type a message…',
}: ChatComposerProps): JSX.Element {
  function handleSubmit(e: FormEvent): void {
    e.preventDefault();
    if (!value.trim() || disabled || isLoading) {
      return;
    }
    onSubmit();
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>): void {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!value.trim() || disabled || isLoading) {
        return;
      }
      onSubmit();
    }
  }

  return (
    <form className={styles.composer} onSubmit={handleSubmit}>
      <label className={styles.srOnly} htmlFor="chat-composer-input">
        Message
      </label>
      <textarea
        id="chat-composer-input"
        aria-label="Message"
        placeholder={placeholder}
        value={value}
        disabled={disabled || isLoading}
        onChange={(ev) => onChange(ev.target.value)}
        onKeyDown={onKeyDown}
        rows={2}
      />
      <Button type="submit" isLoading={isLoading} disabled={disabled || !value.trim()}>
        Send
      </Button>
    </form>
  );
}
