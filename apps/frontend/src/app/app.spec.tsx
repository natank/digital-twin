import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AuthProvider } from '../lib/auth/AuthContext';
import { clearAccessToken } from '../lib/auth/storage';
import { AppRoutes } from './routes';

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('App routes', () => {
  afterEach(() => {
    clearAccessToken();
    vi.unstubAllGlobals();
  });

  it('renders the homepage', async () => {
    renderAt('/');
    expect(await screen.findByRole('heading', { name: /AI professional presence/i })).toBeTruthy();
  });

  it('renders about page', async () => {
    renderAt('/about');
    expect(await screen.findByRole('heading', { name: /About Digital Twin/i })).toBeTruthy();
  });

  it('redirects dashboard to login when unauthenticated', async () => {
    renderAt('/dashboard');
    expect(await screen.findByRole('heading', { name: /Log in/i })).toBeTruthy();
  });
});
