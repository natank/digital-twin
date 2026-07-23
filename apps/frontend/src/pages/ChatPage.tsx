import type { JSX } from 'react';
import { useSearchParams } from 'react-router-dom';

import { ChatWidget } from '../components/chat/ChatWidget';
import styles from './Page.module.css';

export function ChatPage(): JSX.Element {
  const [params] = useSearchParams();
  const ownerFromQuery = params.get('owner') ?? undefined;

  return (
    <section className={styles.page}>
      <h1>Chat</h1>
      <p className={styles.lead}>
        Talk to a digital twin as a visitor. No account required. Replies stream over SSE from the
        Chat API.
      </p>
      <ChatWidget ownerId={ownerFromQuery} />
    </section>
  );
}
