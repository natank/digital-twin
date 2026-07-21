/**
 * Thin fetch wrapper for the Digital Twin API envelope.
 *
 * All backend responses use `{ status, data, error, meta }`
 * (see libs/backend-shared schemas). This client unwraps success
 * payloads and throws {@link ApiClientError} on failures.
 */

import type { ApiEnvelope } from './types';

export class ApiClientError extends Error {
  readonly code: string;
  readonly details: Record<string, unknown>;
  readonly httpStatus: number | undefined;

  constructor(
    code: string,
    message: string,
    details: Record<string, unknown> = {},
    httpStatus?: number,
  ) {
    super(message);
    this.name = 'ApiClientError';
    this.code = code;
    this.details = details;
    this.httpStatus = httpStatus;
  }
}

export function getApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return raw.replace(/\/$/, '');
}

export type ApiFetchOptions = RequestInit & {
  /** Bearer token; when set, sends Authorization header. */
  token?: string | null;
  /** Skip JSON Content-Type (e.g. multipart uploads later). */
  skipJsonContentType?: boolean;
};

/**
 * Perform an API request and return the unwrapped `data` field.
 *
 * @throws {ApiClientError} when the envelope reports error or HTTP fails.
 */
export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { token, skipJsonContentType, headers, body, ...rest } = options;
  const url = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;

  const mergedHeaders: Record<string, string> = {
    ...(skipJsonContentType ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  if (headers) {
    const h = new Headers(headers);
    h.forEach((value, key) => {
      mergedHeaders[key] = value;
    });
  }

  const response = await fetch(url, {
    ...rest,
    headers: mergedHeaders,
    body,
  });

  let envelope: ApiEnvelope<T>;
  try {
    envelope = (await response.json()) as ApiEnvelope<T>;
  } catch {
    throw new ApiClientError(
      'INVALID_RESPONSE',
      `Invalid JSON response (${response.status})`,
      {},
      response.status,
    );
  }

  if (!response.ok || envelope.status === 'error' || envelope.error) {
    throw new ApiClientError(
      envelope.error?.code ?? 'HTTP_ERROR',
      envelope.error?.message ?? (response.statusText || 'Request failed'),
      envelope.error?.details ?? {},
      response.status,
    );
  }

  return envelope.data as T;
}
