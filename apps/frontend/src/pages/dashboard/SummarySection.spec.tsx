import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { SummarySection } from './SummarySection';

describe('SummarySection', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads and saves summary JSON', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/profiles/me/summary') && (!init?.method || init.method === 'GET')) {
        return {
          ok: true,
          status: 200,
          statusText: 'OK',
          json: async () => ({
            status: 'success',
            data: {
              profile_summary: { overview: 'Engineer' },
              skills: ['Python'],
              experience_years: 5,
            },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      if (url.endsWith('/profiles/me/summary') && init?.method === 'PUT') {
        return {
          ok: true,
          status: 200,
          statusText: 'OK',
          json: async () => ({
            status: 'success',
            data: {
              profile_summary: { overview: 'Staff Engineer' },
              skills: ['Python'],
              experience_years: 5,
            },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      throw new Error(`unexpected ${url} ${init?.method}`);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<SummarySection token="tok" />);
    expect(await screen.findByDisplayValue(/Engineer/)).toBeTruthy();
    const area = screen.getByLabelText(/summary json/i);
    await user.clear(area);
    await user.click(area);
    await user.paste('{"overview":"Staff Engineer"}');
    await user.click(screen.getByRole('button', { name: /save summary/i }));
    await waitFor(() => expect(screen.getByText(/summary saved/i)).toBeTruthy());
  });
});
