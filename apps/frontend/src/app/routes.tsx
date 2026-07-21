import type { JSX } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { DashboardLayout } from '../layouts/DashboardLayout';
import { PublicLayout } from '../layouts/PublicLayout';
import { ProtectedRoute } from '../lib/auth/ProtectedRoute';
import { AboutPage } from '../pages/AboutPage';
import { ChatPage } from '../pages/ChatPage';
import { DashboardPage } from '../pages/DashboardPage';
import { ComingSoonPage } from '../pages/dashboard/ComingSoonPage';
import { ForgotPasswordPage } from '../pages/ForgotPasswordPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';
import { ResetPasswordPage } from '../pages/ResetPasswordPage';
import { VerifyEmailPage } from '../pages/VerifyEmailPage';

/** Application route table (Phase 3). */
export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<HomePage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="forgot-password" element={<ForgotPasswordPage />} />
        <Route path="reset-password" element={<ResetPasswordPage />} />
        <Route path="verify-email" element={<VerifyEmailPage />} />
      </Route>

      <Route
        path="dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route
          path="profile"
          element={
            <ComingSoonPage
              title="Profile"
              blurb="Edit your professional profile and CV — landing in PR-007–009."
            />
          }
        />
        <Route
          path="settings"
          element={
            <ComingSoonPage
              title="Settings"
              blurb="Account settings and password options — landing in PR-010."
            />
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
