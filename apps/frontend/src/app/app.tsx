import type { JSX } from 'react';
import { BrowserRouter } from 'react-router-dom';

import { AuthProvider } from '../lib/auth/AuthContext';
import { AppRoutes } from './routes';

export function App(): JSX.Element {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
