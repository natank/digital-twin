import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../../lib/auth/storage';
import { NotificationsPage } from './NotificationsPage';

describe('NotificationsPage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('lists notifications and marks one read', async () => {
    const user = userEvent.setup();
    let read = false;
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        if (url.endsWith('/auth/me')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                id: 'o1',
                email: 'a@b.com',
                first_name: 'Ada',
                last_name: 'L',
                is_active: true,
                email_verified: true,
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.includes('/notifications/me') && url.includes('/read') && init?.method === 'POST') {
          read = true;
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                id: 'n1',
                type: 'conversation_started',
                title: 'New chat',
                message: 'Someone started a chat',
                data: null,
                priority: 0,
                read: true,
                delivery_status: 'sent',
                retry_count: 0,
                created_at: '2026-07-21T12:00:00Z',
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.includes('/notifications/me') && (!init?.method || init.method === 'GET')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                items: [
                  {
                    id: 'n1',
                    type: 'conversation_started',
                    title: 'New chat',
                    message: 'Someone started a chat',
                    data: null,
                    priority: 0,
                    read,
                    delivery_status: 'sent',
                    retry_count: 0,
                    created_at: '2026-07-21T12:00:00Z',
                  },
                ],
                total: 1,
                limit: 50,
                offset: 0,
                unread_count: read ? 0 : 1,
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        throw new Error(`unexpected ${url} ${init?.method}`);
      }),
    );
    setAccessToken('tok');

    render(
      <MemoryRouter>
        <AuthProvider>
          <NotificationsPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText('New chat')).toBeTruthy();
    expect(screen.getByText(/someone started a chat/i)).toBeTruthy();
    await user.click(screen.getByRole('button', { name: /mark read/i }));
    await waitFor(() => expect(screen.queryByRole('button', { name: /mark read/i })).toBeNull());
  });
});
