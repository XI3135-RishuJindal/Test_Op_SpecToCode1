import { Email } from '../email.vo';

describe('Email value object', () => {
  it('normalises to lowercase', () => {
    const email = new Email('Alice@Example.COM');
    expect(email.value).toBe('alice@example.com');
  });

  it('trims whitespace', () => {
    const email = new Email('  bob@example.com  ');
    expect(email.value).toBe('bob@example.com');
  });

  it('throws on invalid format', () => {
    expect(() => new Email('not-an-email')).toThrow();
    expect(() => new Email('@nodomain')).toThrow();
    expect(() => new Email('missing@')).toThrow();
  });

  it('equals returns true for same address', () => {
    const a = new Email('alice@example.com');
    const b = new Email('ALICE@EXAMPLE.COM');
    expect(a.equals(b)).toBe(true);
  });

  it('equals returns false for different addresses', () => {
    const a = new Email('alice@example.com');
    const b = new Email('bob@example.com');
    expect(a.equals(b)).toBe(false);
  });
});
