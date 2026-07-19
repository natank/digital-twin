/**
 * Client-side validation helpers.
 *
 * These mirror `libs/backend-shared/backend_shared/utils.py` so the UI can
 * give immediate feedback. They are a convenience, never a security control —
 * the backend re-validates everything.
 */

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$/;

export const MIN_PASSWORD_LENGTH = 8;

/** Returns whether `email` looks like a valid address. */
export function isValidEmail(email: string): boolean {
  if (!email || email.length > 254) {
    return false;
  }
  return EMAIL_RE.test(email);
}

/**
 * Checks a password against the policy in docs/PRD.md (E1-S1).
 *
 * @returns Human-readable problems; an empty array means the password passes.
 */
export function validatePasswordStrength(password: string): string[] {
  const problems: string[] = [];
  if (password.length < MIN_PASSWORD_LENGTH) {
    problems.push(`Password must be at least ${MIN_PASSWORD_LENGTH} characters`);
  }
  if (!/[A-Z]/.test(password)) {
    problems.push('Password must contain an uppercase letter');
  }
  if (!/[0-9]/.test(password)) {
    problems.push('Password must contain a number');
  }
  if (!/[^a-zA-Z0-9]/.test(password)) {
    problems.push('Password must contain a special character');
  }
  return problems;
}

/** Convenience wrapper around {@link validatePasswordStrength}. */
export function isStrongPassword(password: string): boolean {
  return validatePasswordStrength(password).length === 0;
}

/** Returns whether `value` is non-empty once surrounding whitespace is ignored. */
export function isNonEmpty(value: string): boolean {
  return value.trim().length > 0;
}
