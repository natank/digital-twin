import { fireEvent, render, screen, waitFor } from '@testing-library/react';
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

  it('stops polling and surfaces an error when a job never leaves pending', async () => {
    vi.useFakeTimers();
    try {
      const onRefresh = vi.fn();
      let statusCalls = 0;
      const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith('/profiles/me/process-cv')) {
          return {
            ok: true,
            status: 202,
            statusText: 'Accepted',
            json: async () => ({
              status: 'success',
              data: {
                id: 'job-1',
                owner_id: 'o1',
                status: 'pending',
                cv_file_path: 's3://b/cv.pdf',
                error_message: null,
                created_at: 't',
                updated_at: 't',
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        if (url.includes('/profiles/me/cv/jobs/')) {
          statusCalls += 1;
          return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => ({
              status: 'success',
              data: {
                id: 'job-1',
                owner_id: 'o1',
                status: 'pending',
                cv_file_path: 's3://b/cv.pdf',
                error_message: null,
                created_at: 't',
                updated_at: 't',
              },
              error: null,
              meta: { timestamp: 't', request_id: null },
            }),
          };
        }
        throw new Error(`unexpected ${url}`);
      });
      vi.stubGlobal('fetch', fetchMock);

      render(
        <CvUploadSection
          token="tok"
          profile={{ ...baseProfile, has_cv: true }}
          onProfileRefresh={onRefresh}
        />,
      );

      fireEvent.click(screen.getByRole('button', { name: /process cv/i }));

      // Advance well past the 2-minute poll timeout.
      await vi.advanceTimersByTimeAsync(130_000);

      expect(screen.getByRole('alert').textContent).toMatch(/taking longer than expected/i);
      const callsAtTimeout = statusCalls;
      // No further polling after the timeout fires.
      await vi.advanceTimersByTimeAsync(10_000);
      expect(statusCalls).toBe(callsAtTimeout);
    } finally {
      vi.useRealTimers();
    }
  });
});
