import type { JSX } from 'react';
import { BrowserRouter } from 'react-router-dom';

import { AuthProvider } from '../lib/auth/AuthContext';
import { NotificationsProvider } from '../lib/notifications/NotificationsContext';
import { AppRoutes } from './routes';

export function App(): JSX.Element {
  return (
    <BrowserRouter>
      <AuthProvider>
        <NotificationsProvider>
          <AppRoutes />
        </NotificationsProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
