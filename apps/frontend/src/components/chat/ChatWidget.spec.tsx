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

function sessionFetchMock() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.includes('/chat/sessions') && init?.method === 'POST' && !url.includes('/sse')) {
      const body = JSON.parse(String(init.body));
      return {
        ok: true,
        status: 201,
        statusText: 'Created',
        json: async () => ({
          status: 'success',
          data: {
            session_id: `sess-${body.owner_id}`,
            owner_id: body.owner_id,
            expires_at: '2099-01-01T00:00:00Z',
            owner_first_name: 'Ada',
            owner_headline: 'Engineer',
          },
          error: null,
          meta: { timestamp: 't', request_id: null },
        }),
      };
    }
    throw new Error(`Unexpected fetch ${url}`);
  });
}

describe('ChatWidget', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows setup hint when no owner id and no demo fallback configured', () => {
    render(<ChatWidget ownerId="" />);
    expect(screen.getByText(/VITE_DEMO_OWNER_ID/i)).toBeTruthy();
  });

  it('shows a sample-mode banner (no raw owner id) when falling back to the demo owner', async () => {
    vi.stubGlobal('fetch', sessionFetchMock());
    vi.stubEnv('VITE_DEMO_OWNER_ID', 'demo-owner');

    render(<ChatWidget />);

    expect(await screen.findByText(/sample twin/i)).toBeTruthy();
    expect(screen.queryByText(/previewing as/i)).toBeNull();
  });

  it('does not show the sample-mode banner when an owner id is explicit', async () => {
    vi.stubGlobal('fetch', sessionFetchMock());

    render(<ChatWidget ownerId="owner-1" />);

    await waitFor(() => expect(screen.getByText(/Chat with Ada|Ada · Engineer/i)).toBeTruthy());
    expect(screen.queryByText(/sample twin/i)).toBeNull();
  });

  it('hides the raw owner id from regular visitors, and keeps the switcher collapsed by default', async () => {
    vi.stubGlobal('fetch', sessionFetchMock());

    render(<ChatWidget ownerId="owner-1" />);

    await waitFor(() => expect(screen.getByText(/Chat with Ada|Ada · Engineer/i)).toBeTruthy());
    expect(screen.queryByText(/previewing as/i)).toBeNull();
    expect(screen.getByRole('button', { name: /switch owner/i })).toBeTruthy();
    expect(screen.queryByRole('textbox', { name: /switch owner/i })).toBeNull();
  });

  it('reveals the owner switcher on toggle click and hides it again on cancel', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', sessionFetchMock());

    render(<ChatWidget ownerId="owner-1" />);
    await waitFor(() => expect(screen.getByText(/Chat with Ada|Ada · Engineer/i)).toBeTruthy());

    await user.click(screen.getByRole('button', { name: /switch owner/i }));
    expect(screen.getByRole('textbox', { name: /switch owner/i })).toBeTruthy();

    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(screen.queryByRole('textbox', { name: /switch owner/i })).toBeNull();
  });

  it('shows owner id in preview mode, and lets any visitor switch owner profiles via the toggle', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', sessionFetchMock());
    vi.stubEnv('VITE_DEMO_OWNER_ID', 'demo-owner');

    render(<ChatWidget preview />);
    expect(await screen.findByText(/sample twin/i)).toBeTruthy();
    expect(screen.getByText(/previewing as/i).textContent).toContain('demo-owner');

    await user.click(screen.getByRole('button', { name: /switch owner/i }));
    await user.type(screen.getByRole('textbox', { name: /switch owner/i }), 'owner-42');
    await user.click(screen.getByRole('button', { name: /^switch$/i }));

    await waitFor(() =>
      expect(screen.getByText(/previewing as/i).textContent).toContain('owner-42'),
    );
    expect(screen.queryByText(/sample twin/i)).toBeNull();
    expect(screen.queryByRole('textbox', { name: /switch owner/i })).toBeNull();
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

    await user.type(screen.getByRole('textbox', { name: /message/i }), 'Hello');
    await user.click(screen.getByRole('button', { name: /send/i }));
    expect(await screen.findByText('Hello')).toBeTruthy();
    expect(await screen.findByText('Hi there!')).toBeTruthy();
  });

  it('shows retry when session start fails', async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        json: async () => ({
          status: 'error',
          data: null,
          error: { code: 'ERR', message: 'Backend down', details: {} },
          meta: { timestamp: 't', request_id: null },
        }),
      }),
    );
    render(<ChatWidget ownerId="owner-1" />);
    expect(await screen.findByText(/backend down/i)).toBeTruthy();
    expect(screen.getByRole('button', { name: /retry connection/i })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(screen.queryByText(/backend down/i)).toBeNull();
  });
});
