import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../../lib/auth/storage';
import { PushoverPage } from './PushoverPage';

describe('PushoverPage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('saves pushover config', async () => {
    const user = userEvent.setup();
    let configured = false;
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
        if (url.includes('/preferences')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: { global_push_enabled: true, types: {} },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.includes('/pushover') && init?.method === 'PUT') {
          configured = true;
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                configured: true,
                enabled: true,
                device: null,
                sound: 'pushover',
                user_key_masked: 'u***key',
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.includes('/pushover')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                configured,
                enabled: configured,
                device: null,
                sound: configured ? 'pushover' : null,
                user_key_masked: configured ? 'u***key' : null,
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
      <MemoryRouter>
        <AuthProvider>
          <PushoverPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /pushover setup/i })).toBeTruthy();
    await user.type(screen.getByLabelText(/user key/i), 'valid-user-key-12345');
    await user.click(screen.getByRole('button', { name: /^save$/i }));
    await waitFor(() => expect(screen.getByText(/settings saved/i)).toBeTruthy());
  });
});
