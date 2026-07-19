/**
 * Shared frontend library for the Digital Twin platform.
 *
 * Contains presentational components, validation helpers, and the
 * TypeScript types mirroring the backend API.
 *
 * Not yet included: `useAuth`/`useApi` hooks, which depend on auth and API
 * contracts that land in Phase 1 (see docs/phase-0/PR_BREAKDOWN.md, PR-005
 * notes).
 */

export * from './components';
export * from './types';
export * from './utils';
