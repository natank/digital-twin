/**
 * Auth session context for the SPA.
 *
 * Loads `/auth/me` when a stored token exists; exposes login/logout helpers.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type JSX,
  type ReactNode,
} from 'react';

import { loginRequest, logoutRequest, meRequest, registerRequest } from '../api/auth';
import type { OwnerWire } from '../api/types';
import { ApiClientError } from '../api/client';
import { clearAccessToken, getAccessToken, setAccessToken } from './storage';

export interface AuthContextValue {
  owner: OwnerWire | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (input: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [owner, setOwner] = useState<OwnerWire | null>(null);
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [isLoading, setIsLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const current = getAccessToken();
    if (!current) {
      setOwner(null);
      setToken(null);
      return;
    }
    try {
      const me = await meRequest(current);
      setOwner(me);
      setToken(current);
    } catch (err) {
      // Stale/invalid token — clear session.
      if (err instanceof ApiClientError && (err.httpStatus === 401 || err.httpStatus === 403)) {
        clearAccessToken();
        setOwner(null);
        setToken(null);
        return;
      }
      throw err;
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (getAccessToken()) {
          await refreshMe();
        }
      } catch {
        // Network blip on boot: leave token, no owner until retry.
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [refreshMe]);

  const login = useCallback(async (email: string, password: string) => {
    const result = await loginRequest({ email, password });
    setAccessToken(result.access_token);
    setToken(result.access_token);
    setOwner(result.owner);
  }, []);

  const register = useCallback(
    async (input: { email: string; password: string; firstName: string; lastName: string }) => {
      await registerRequest({
        email: input.email,
        password: input.password,
        first_name: input.firstName,
        last_name: input.lastName,
      });
      // Auto-login after successful registration.
      await login(input.email, input.password);
    },
    [login],
  );

  const logout = useCallback(async () => {
    const current = getAccessToken();
    if (current) {
      try {
        await logoutRequest(current);
      } catch {
        // Still clear local session if server logout fails.
      }
    }
    clearAccessToken();
    setToken(null);
    setOwner(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      owner,
      token,
      isLoading,
      isAuthenticated: Boolean(token && owner),
      login,
      register,
      logout,
      refreshMe,
    }),
    [owner, token, isLoading, login, register, logout, refreshMe],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook co-located with provider (react-refresh only cares about component exports).
// eslint-disable-next-line react-refresh/only-export-components -- useAuth is the public API
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
