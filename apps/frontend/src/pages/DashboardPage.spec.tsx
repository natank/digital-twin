import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../lib/auth/storage';
import { DashboardPage } from './DashboardPage';

describe('DashboardPage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('links "Public chat" to the current owner id, not the bare demo route', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({
          status: 'success',
          data: {
            id: 'owner-123',
            email: 'owner@example.com',
            first_name: 'Ada',
            last_name: 'Lovelace',
            is_active: true,
            email_verified: true,
          },
          error: null,
          meta: { timestamp: 't', request_id: null },
        }),
      }),
    );
    setAccessToken('tok');

    render(
      <MemoryRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    const link = await screen.findByRole('link', { name: /public chat/i });
    expect(link.getAttribute('href')).toBe('/chat?owner=owner-123&preview=1');
  });
});
