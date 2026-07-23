import { afterEach, describe, expect, it, vi } from 'vitest';

import { prefersReducedMotion, scrollBehavior } from './chatA11y';

describe('chatA11y', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('detects reduced motion', () => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockReturnValue({ matches: true, media: '(prefers-reduced-motion: reduce)' }),
    );
    expect(prefersReducedMotion()).toBe(true);
    expect(scrollBehavior()).toBe('auto');
  });

  it('allows smooth scroll when motion is ok', () => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockReturnValue({ matches: false, media: '(prefers-reduced-motion: reduce)' }),
    );
    expect(prefersReducedMotion()).toBe(false);
    expect(scrollBehavior()).toBe('smooth');
  });
});
