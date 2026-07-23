import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { MessageBubble } from './MessageBubble';

describe('MessageBubble', () => {
  it('renders visitor content and timestamp', () => {
    render(
      <MessageBubble
        message={{
          id: '1',
          sender: 'visitor',
          content: 'Hello there',
          created_at: '2026-07-21T12:30:00.000Z',
        }}
      />,
    );
    expect(screen.getByText('Hello there')).toBeTruthy();
    expect(screen.getByRole('article', { name: /you message/i })).toBeTruthy();
    expect(screen.getByText(/:/)).toBeTruthy(); // locale time
  });

  it('renders AI bubble', () => {
    render(
      <MessageBubble
        message={{
          id: '2',
          sender: 'ai',
          content: 'Hi!',
        }}
      />,
    );
    expect(screen.getByRole('article', { name: /digital twin message/i })).toBeTruthy();
  });
});
