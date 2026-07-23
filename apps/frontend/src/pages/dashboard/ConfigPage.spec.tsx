import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../../lib/auth/AuthContext';
import { clearAccessToken, setAccessToken } from '../../lib/auth/storage';
import { ConfigPage } from './ConfigPage';

describe('ConfigPage', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('loads and saves twin config', async () => {
    const user = userEvent.setup();
    let tone = 'professional';
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
        if (url.includes('/versions') && !url.includes('restore')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: { versions: [] },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.endsWith('/config/me') && init?.method === 'PUT') {
          const body = JSON.parse(String(init.body)) as { tone?: string };
          tone = body.tone ?? tone;
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                id: 'c1',
                owner_id: 'o1',
                system_prompt: 'You are {owner_name}.\n{profile_summary}',
                tone,
                response_length: 'balanced',
                allowed_topics: ['Python'],
                forbidden_topics: [],
                brand_guidelines: null,
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.endsWith('/config/me')) {
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                id: 'c1',
                owner_id: 'o1',
                system_prompt: 'You are {owner_name}.\n{profile_summary}',
                tone,
                response_length: 'balanced',
                allowed_topics: ['Python'],
                forbidden_topics: [],
                brand_guidelines: null,
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
          <ConfigPage />
        </AuthProvider>
      </MemoryRouter>,
    );

    expect(await screen.findByDisplayValue(/You are \{owner_name\}/)).toBeTruthy();
    await user.selectOptions(screen.getByLabelText(/^tone$/i), 'friendly');
    await user.click(screen.getByRole('button', { name: /save config/i }));
    await waitFor(() => expect(screen.getByText(/configuration saved/i)).toBeTruthy());
  });
});
