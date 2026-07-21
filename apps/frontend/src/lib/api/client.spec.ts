import { afterEach, describe, expect, it, vi } from 'vitest';

import { ApiClientError, apiFetch, getApiBaseUrl } from './client';

describe('getApiBaseUrl', () => {
  it('returns a non-empty default', () => {
    expect(getApiBaseUrl().length).toBeGreaterThan(0);
  });
});

describe('apiFetch', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('unwraps success data', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({
          status: 'success',
          data: { id: '1', email: 'a@b.com' },
          error: null,
          meta: { timestamp: '2026-01-01T00:00:00Z', request_id: null },
        }),
      }),
    );

    const data = await apiFetch<{ id: string; email: string }>('/auth/me', {
      token: 'tok',
    });
    expect(data.email).toBe('a@b.com');
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/me'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer tok',
          'Content-Type': 'application/json',
        }),
      }),
    );
  });

  it('throws ApiClientError on envelope error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({
          status: 'error',
          data: null,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Invalid credentials',
            details: {},
          },
          meta: { timestamp: '2026-01-01T00:00:00Z', request_id: null },
        }),
      }),
    );

    await expect(apiFetch('/auth/login', { method: 'POST' })).rejects.toMatchObject({
      name: 'ApiClientError',
      code: 'UNAUTHORIZED',
      message: 'Invalid credentials',
      httpStatus: 401,
    });
    await expect(apiFetch('/auth/login', { method: 'POST' })).rejects.toBeInstanceOf(
      ApiClientError,
    );
  });

  it('throws on invalid JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        statusText: 'Bad Gateway',
        json: async () => {
          throw new Error('not json');
        },
      }),
    );

    await expect(apiFetch('/health')).rejects.toMatchObject({
      code: 'INVALID_RESPONSE',
    });
  });
});
