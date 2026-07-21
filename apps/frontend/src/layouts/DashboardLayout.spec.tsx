import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../lib/auth/storage';
import { DashboardLayout } from './DashboardLayout';

describe('DashboardLayout', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('renders sidebar nav and user menu logout', async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
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
      }),
    );
    setAccessToken('tok');

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider>
          <Routes>
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<h1>Overview</h1>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByRole('link', { name: /overview/i })).toBeTruthy();
    expect(screen.getByRole('link', { name: /^profile$/i })).toBeTruthy();
    expect(screen.getByRole('link', { name: /^settings$/i })).toBeTruthy();

    await user.click(await screen.findByRole('button', { name: /ada lovelace/i }));
    expect(screen.getByRole('menuitem', { name: /log out/i })).toBeTruthy();
  });
});
