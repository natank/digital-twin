// Uncomment this line to use CSS modules
// import styles from './app.module.css';
import type { JSX } from 'react';

import NxWelcome from './nx-welcome';

export function App(): JSX.Element {
  return (
    <div>
      <NxWelcome title="frontend" />
    </div>
  );
}

export default App;
