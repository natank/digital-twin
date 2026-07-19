/**
 * Shared TypeScript types.
 *
 * These mirror the backend's models and API envelope
 * (see docs/TECHNICAL_DESIGN.md). Keep them in sync with
 * `apps/backend/src/db/models.py` and `libs/backend-shared/schemas.py`.
 */

/** A registered professional whose digital twin is hosted on the platform. */
export interface Owner {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

/** An owner's professional profile, largely derived from their CV. */
export interface Profile {
  id: string;
  ownerId: string;
  bio: string | null;
  headline: string | null;
  profileSummary: Record<string, unknown> | null;
  skills: string[] | null;
  experienceYears: number | null;
  createdAt: string;
  updatedAt: string;
}

/** Error payload carried by an error response. */
export interface ApiError {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

/** Per-response metadata for tracing and debugging. */
export interface ResponseMeta {
  timestamp: string;
  requestId: string | null;
}

/** Envelope wrapping every API response. */
export interface ApiResponse<T> {
  status: 'success' | 'error';
  data: T | null;
  error: ApiError | null;
  meta: ResponseMeta;
}

/** Pagination metadata for list endpoints. */
export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

/** Who produced a chat message. */
export type MessageSender = 'visitor' | 'ai';

/** A single message within a chat session. */
export interface ChatMessage {
  id: string;
  sessionId: string;
  sender: MessageSender;
  content: string;
  createdAt: string;
}
