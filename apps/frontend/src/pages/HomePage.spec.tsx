import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { AuthProvider } from '../lib/auth/AuthContext';
import { HomePage } from './HomePage';

describe('HomePage', () => {
  it('renders hero and primary CTAs', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <HomePage />
        </AuthProvider>
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: /AI professional presence/i })).toBeTruthy();
    expect(screen.getByRole('link', { name: /demo chat/i })).toBeTruthy();
    expect(screen.getByRole('link', { name: /create an account/i })).toBeTruthy();
    expect(screen.getByRole('list', { name: /product highlights/i })).toBeTruthy();
  });
});
