import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../../lib/auth/storage';
import { ProfilePage } from './ProfilePage';

describe('ProfilePage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('loads profile and saves edits', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
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
      if (url.endsWith('/profiles/me') && (!init?.method || init.method === 'GET')) {
        return {
          ok: true,
          status: 200,
          statusText: 'OK',
          json: async () => ({
            status: 'success',
            data: {
              id: 'p1',
              owner_id: 'o1',
              bio: 'Old bio',
              headline: 'Engineer',
              skills: ['Python'],
              experience_years: 5,
              profile_summary: null,
              has_cv: false,
              has_extracted_text: false,
            },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      if (url.endsWith('/profiles/me') && init?.method === 'PUT') {
        const body = JSON.parse(String(init.body)) as { headline: string };
        return {
          ok: true,
          status: 200,
          statusText: 'OK',
          json: async () => ({
            status: 'success',
            data: {
              id: 'p1',
              owner_id: 'o1',
              bio: 'Old bio',
              headline: body.headline,
              skills: ['Python', 'React'],
              experience_years: 5,
              profile_summary: null,
              has_cv: false,
              has_extracted_text: false,
            },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      throw new Error(`unexpected ${url} ${init?.method}`);
    });
    vi.stubGlobal('fetch', fetchMock);
    setAccessToken('tok');

    render(
      <MemoryRouter>
        <AuthProvider>
          <ProfilePage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByDisplayValue('Engineer')).toBeTruthy();
    const headline = screen.getByLabelText(/headline/i);
    await user.clear(headline);
    await user.type(headline, 'Staff Engineer');
    await user.click(screen.getByRole('button', { name: /save profile/i }));
    await waitFor(() => expect(screen.getByText(/profile saved/i)).toBeTruthy());
  });
});
