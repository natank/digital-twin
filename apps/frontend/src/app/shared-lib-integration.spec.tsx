/**
 * Verifies the frontend app can consume `frontend-shared`.
 *
 * This is the PR-005 acceptance criterion "can be used by other packages".
 * Real UI usage of these components arrives in Phase 3; this test exists so
 * the wiring (workspace dependency + TS project reference) can't silently
 * break before then.
 */
import { render, screen } from '@testing-library/react';
import { Button, Input, isValidEmail, type Owner } from 'frontend-shared';

describe('frontend-shared integration', () => {
  it('renders a shared Button', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeTruthy();
  });

  it('renders a shared Input', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText('Email')).toBeTruthy();
  });

  it('uses shared validators', () => {
    expect(isValidEmail('user@example.com')).toBe(true);
    expect(isValidEmail('nope')).toBe(false);
  });

  it('uses shared types', () => {
    const owner: Owner = {
      id: 'a1',
      email: 'owner@example.com',
      firstName: 'Sample',
      lastName: 'Owner',
      isActive: true,
      emailVerified: true,
      createdAt: '2026-01-01T00:00:00Z',
      updatedAt: '2026-01-01T00:00:00Z',
    };
    expect(owner.email).toBe('owner@example.com');
  });
});
