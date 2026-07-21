import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../../lib/auth/storage';
import { SettingsPage } from './SettingsPage';

describe('SettingsPage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it('shows account info and requests password reset', async () => {
    const user = userEvent.setup();
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
                email: 'owner@example.com',
                first_name: 'Ada',
                last_name: 'Lovelace',
                is_active: true,
                email_verified: true,
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.endsWith('/auth/forgot-password') && init?.method === 'POST') {
          return {
            ok: true,
            status: 202,
            statusText: 'Accepted',
            json: async () => ({
              status: 'success',
              data: { message: 'ok' },
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
      <MemoryRouter>
        <AuthProvider>
          <SettingsPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByText('owner@example.com')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: /email password reset/i }));
    await waitFor(() => expect(screen.getByText(/reset email was sent/i)).toBeTruthy());
  });
});
