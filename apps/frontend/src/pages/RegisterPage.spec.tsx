import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { AuthProvider } from '../lib/auth/AuthContext';
import { RegisterPage } from './RegisterPage';

describe('RegisterPage', () => {
  it('rejects weak passwords', async () => {
    const user = userEvent.setup();
    const { container } = render(
      <MemoryRouter>
        <AuthProvider>
          <RegisterPage />
        </AuthProvider>
      </MemoryRouter>,
    );
    await user.type(screen.getByLabelText(/first name/i), 'Ada');
    await user.type(screen.getByLabelText(/last name/i), 'Lovelace');
    await user.type(screen.getByLabelText(/email/i), 'ada@example.com');
    const passwordInput = container.querySelector('input[name="password"]');
    expect(passwordInput).toBeTruthy();
    await user.type(passwordInput as HTMLInputElement, 'weak');
    await user.click(screen.getByRole('button', { name: /register/i }));
    expect(await screen.findByText(/at least 8 characters|uppercase|number|special/i)).toBeTruthy();
  });
});
