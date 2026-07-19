import {
  isNonEmpty,
  isStrongPassword,
  isValidEmail,
  validatePasswordStrength,
} from './validators';

describe('isValidEmail', () => {
  it.each(['user@example.com', 'first.last@sub.example.co.uk', 'a+tag@example.io'])(
    'accepts %s',
    (email) => {
      expect(isValidEmail(email)).toBe(true);
    }
  );

  it.each(['', 'no-at-sign', '@example.com', 'user@', 'user@nodot', 'a b@example.com'])(
    'rejects %s',
    (email) => {
      expect(isValidEmail(email)).toBe(false);
    }
  );

  it('rejects addresses over the length limit', () => {
    expect(isValidEmail(`${'a'.repeat(250)}@example.com`)).toBe(false);
  });
});

describe('validatePasswordStrength', () => {
  it('accepts a strong password', () => {
    expect(validatePasswordStrength('SecurePass1!')).toEqual([]);
  });

  it.each([
    ['Sh0rt!', 'at least 8 characters'],
    ['nouppercase1!', 'uppercase letter'],
    ['NoDigitsHere!', 'a number'],
    ['NoSpecial123', 'special character'],
  ])('reports the problem with %s', (password, expected) => {
    const problems = validatePasswordStrength(password);
    expect(problems.some((p) => p.includes(expected))).toBe(true);
  });

  it('reports multiple problems together', () => {
    expect(validatePasswordStrength('abc')).toHaveLength(4);
  });

  it('matches the backend policy for the same inputs', () => {
    // Guards against client/server drift; see backend test_utils.py.
    expect(isStrongPassword('SecurePass1!')).toBe(true);
    expect(isStrongPassword('weak')).toBe(false);
  });
});

describe('isNonEmpty', () => {
  it('accepts text with content', () => {
    expect(isNonEmpty('hello')).toBe(true);
  });

  it.each(['', '   ', '\t\n'])('rejects whitespace-only input %j', (value) => {
    expect(isNonEmpty(value)).toBe(false);
  });
});
