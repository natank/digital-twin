import type { JSX } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { PublicLayout } from '../layouts/PublicLayout';
import { ProtectedRoute } from '../lib/auth/ProtectedRoute';
import { AboutPage } from '../pages/AboutPage';
import { HomePage } from '../pages/HomePage';
import { PlaceholderPage } from '../pages/PlaceholderPage';

/**
 * Application route table (Phase 3 Week 11 shell).
 * Auth forms, full chat, and dashboard content land in PR-002–005.
 */
export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<HomePage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="chat" element={<PlaceholderPage title="Chat" />} />
        <Route path="login" element={<PlaceholderPage title="Log in" />} />
        <Route path="register" element={<PlaceholderPage title="Register" />} />
        <Route path="forgot-password" element={<PlaceholderPage title="Forgot password" />} />
        <Route path="reset-password" element={<PlaceholderPage title="Reset password" />} />
        <Route path="verify-email" element={<PlaceholderPage title="Verify email" />} />
        <Route
          path="dashboard"
          element={
            <ProtectedRoute>
              <PlaceholderPage title="Dashboard" />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
