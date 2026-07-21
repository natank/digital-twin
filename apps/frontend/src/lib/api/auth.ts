/** Auth API helpers. */

import { apiFetch } from './client';
import type { OwnerWire, TokenResponseWire } from './types';

export interface LoginBody {
  email: string;
  password: string;
}

export interface RegisterBody {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export function loginRequest(body: LoginBody): Promise<TokenResponseWire> {
  return apiFetch<TokenResponseWire>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function registerRequest(body: RegisterBody): Promise<OwnerWire> {
  return apiFetch<OwnerWire>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function meRequest(token: string): Promise<OwnerWire> {
  return apiFetch<OwnerWire>('/auth/me', { token });
}

export function logoutRequest(token: string): Promise<{ message?: string } | null> {
  return apiFetch('/auth/logout', { method: 'POST', token });
}

export function forgotPasswordRequest(email: string): Promise<{ message?: string } | null> {
  return apiFetch('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export function resetPasswordRequest(
  token: string,
  new_password: string,
): Promise<{ message?: string } | null> {
  return apiFetch('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password }),
  });
}

export function verifyEmailRequest(token: string): Promise<{ message?: string } | null> {
  return apiFetch('/auth/verify-email', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
}
