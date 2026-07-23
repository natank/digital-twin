import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { ChatWidget } from './ChatWidget';

function sseStream(events: string): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(events));
      controller.close();
    },
  });
}

describe('ChatWidget', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows setup hint when no owner id', () => {
    render(<ChatWidget ownerId="" />);
    expect(screen.getByText(/VITE_DEMO_OWNER_ID/i)).toBeTruthy();
  });

  it('creates a session and streams a reply', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes('/chat/sessions') && init?.method === 'POST' && !url.includes('/sse')) {
        return {
          ok: true,
          status: 201,
          statusText: 'Created',
          json: async () => ({
            status: 'success',
            data: {
              session_id: 'sess-1',
              owner_id: 'owner-1',
              expires_at: '2099-01-01T00:00:00Z',
              owner_first_name: 'Ada',
              owner_headline: 'Engineer',
            },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      if (url.includes('/sse/') && init?.method === 'POST') {
        return {
          ok: true,
          status: 200,
          body: sseStream(
            [
              'event: meta',
              'data: {"boundary_redirect": false}',
              '',
              'event: token',
              'data: Hi there!',
              '',
              'event: done',
              'data: {"status":"completed"}',
              '',
            ].join('\n'),
          ),
        };
      }
      throw new Error(`Unexpected fetch ${url}`);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<ChatWidget ownerId="owner-1" />);
    await waitFor(() => expect(screen.getByText(/Chat with Ada|Ada · Engineer/i)).toBeTruthy());

    await user.type(screen.getByLabelText(/message/i), 'Hello');
    await user.click(screen.getByRole('button', { name: /send/i }));
    expect(await screen.findByText('Hello')).toBeTruthy();
    expect(await screen.findByText('Hi there!')).toBeTruthy();
  });
});
