import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../../lib/auth/storage';
import { ConversationsPage } from './ConversationsPage';

describe('ConversationsPage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('lists conversations', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL) => {
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
        if (url.includes('/chat/me/conversations')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                items: [
                  {
                    session_id: 'sess-abc',
                    created_at: '2026-07-21T10:00:00Z',
                    expires_at: '2099-01-01T00:00:00Z',
                    flagged: false,
                    message_count: 2,
                    preview: 'What is your background?',
                    last_message_at: '2026-07-21T10:05:00Z',
                  },
                ],
                total: 1,
                limit: 50,
                offset: 0,
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        throw new Error(`unexpected ${url}`);
      }),
    );
    setAccessToken('tok');

    render(
      <MemoryRouter initialEntries={['/dashboard/conversations']}>
        <AuthProvider>
          <Routes>
            <Route path="/dashboard/conversations/*" element={<ConversationsPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText(/what is your background/i)).toBeTruthy());
  });
});
