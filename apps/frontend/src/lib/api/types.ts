/**
 * Wire-format types matching backend JSON (snake_case).
 *
 * Prefer these at the API boundary. Shared camelCase types in
 * `frontend-shared` remain available for UI-facing models.
 */

export interface ApiErrorBody {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ResponseMeta {
  timestamp: string;
  request_id: string | null;
}

export interface ApiEnvelope<T> {
  status: 'success' | 'error';
  data: T | null;
  error: ApiErrorBody | null;
  meta: ResponseMeta;
}

/** Owner as returned by `/auth/*` endpoints. */
export interface OwnerWire {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  email_verified: boolean;
  oauth_provider?: string | null;
  created_at?: string | null;
}

export interface TokenResponseWire {
  access_token: string;
  token_type: string;
  expires_at: string;
  owner: OwnerWire;
}
