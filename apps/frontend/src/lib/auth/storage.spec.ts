import { beforeEach, describe, expect, it } from 'vitest';

import { clearAccessToken, getAccessToken, setAccessToken } from './storage';

describe('auth storage', () => {
  beforeEach(() => {
    clearAccessToken();
  });

  it('round-trips a token', () => {
    expect(getAccessToken()).toBeNull();
    setAccessToken('abc.def.ghi');
    expect(getAccessToken()).toBe('abc.def.ghi');
    clearAccessToken();
    expect(getAccessToken()).toBeNull();
  });
});
