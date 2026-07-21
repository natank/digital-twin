import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import type { ProfileWire } from '../../lib/api/profiles';
import { CvUploadSection } from './CvUploadSection';

const baseProfile: ProfileWire = {
  id: 'p1',
  owner_id: 'o1',
  bio: null,
  headline: null,
  skills: null,
  experience_years: null,
  profile_summary: null,
  has_cv: false,
  has_extracted_text: false,
};

describe('CvUploadSection', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('uploads a file and refreshes profile', async () => {
    const user = userEvent.setup();
    const onRefresh = vi.fn();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/profiles/me/cv') && init?.method === 'POST') {
        return {
          ok: true,
          status: 201,
          statusText: 'Created',
          json: async () => ({
            status: 'success',
            data: {
              cv_file_path: 's3://b/cv.pdf',
              filename: 'cv.pdf',
              content_type: 'application/pdf',
              size_bytes: 12,
            },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      if (url.endsWith('/profiles/me')) {
        return {
          ok: true,
          status: 200,
          statusText: 'OK',
          json: async () => ({
            status: 'success',
            data: { ...baseProfile, has_cv: true },
            error: null,
            meta: { timestamp: 't', request_id: null },
          }),
        };
      }
      throw new Error(`unexpected ${url}`);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<CvUploadSection token="tok" profile={baseProfile} onProfileRefresh={onRefresh} />);

    const file = new File(['%PDF-1.4'], 'cv.pdf', { type: 'application/pdf' });
    await user.upload(screen.getByLabelText(/cv file/i), file);
    await user.click(screen.getByRole('button', { name: /^upload$/i }));
    await waitFor(() => expect(screen.getByText(/uploaded cv\.pdf/i)).toBeTruthy());
    expect(onRefresh).toHaveBeenCalled();
  });
});
