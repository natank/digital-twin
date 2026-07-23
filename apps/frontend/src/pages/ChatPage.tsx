import type { JSX } from 'react';
import { useSearchParams } from 'react-router-dom';

import { ChatWidget } from '../components/chat/ChatWidget';
import styles from './Page.module.css';

export function ChatPage(): JSX.Element {
  const [params] = useSearchParams();
  const ownerFromQuery = params.get('owner') ?? undefined;

  return (
    <section className={`${styles.page} ${styles.chatPage}`} aria-labelledby="chat-page-heading">
      <h1 id="chat-page-heading">Chat</h1>
      <p className={styles.lead}>
        Talk to a digital twin as a visitor. No account required. Replies stream over SSE from the
        Chat API.
      </p>
      <a className={styles.skipToChat} href="#chat-composer-input">
        Skip to message input
      </a>
      <ChatWidget ownerId={ownerFromQuery} />
    </section>
  );
}
