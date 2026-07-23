import { afterEach, describe, expect, it, vi } from 'vitest';

import { ChatStreamError, streamChatReply } from './chatStream';

function sseBody(events: string): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(events));
      controller.close();
    },
  });
}

describe('streamChatReply', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('parses meta, tokens, and done', async () => {
    const tokens: string[] = [];
    let boundary = false;
    let done = false;

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        body: sseBody(
          [
            'event: meta',
            'data: {"boundary_redirect": true}',
            '',
            'event: token',
            'data: Hello',
            '',
            'event: token',
            'data:  world',
            '',
            'event: done',
            'data: {"status":"completed"}',
            '',
          ].join('\n'),
        ),
      }),
    );

    await streamChatReply('sess-1', 'Hi', {
      onMeta: (m) => {
        boundary = m.boundary_redirect;
      },
      onToken: (t) => tokens.push(t),
      onDone: () => {
        done = true;
      },
    });

    expect(boundary).toBe(true);
    expect(tokens.join('')).toBe('Hello world');
    expect(done).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/chat/sse/sess-1/stream'),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('throws ChatStreamError on HTTP failure', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        json: async () => ({
          error: { message: 'Rate limited' },
        }),
      }),
    );

    await expect(streamChatReply('s', 'x', { onToken: () => undefined })).rejects.toBeInstanceOf(
      ChatStreamError,
    );
    await expect(streamChatReply('s', 'x', { onToken: () => undefined })).rejects.toMatchObject({
      message: 'Rate limited',
      httpStatus: 429,
    });
  });
});
