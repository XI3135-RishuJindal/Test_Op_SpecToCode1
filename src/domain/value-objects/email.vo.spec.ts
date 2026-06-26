import { Email } from '../../domain/value-objects/email.vo';

describe('Email value object', () => {
  it('should create a valid email and normalise to lowercase', () => {
    const email = Email.create('User@Example.COM');
    expect(email.value).toBe('user@example.com');
  });

  it('should trim whitespace', () => {
    const email = Email.create('  hello@world.io  ');
    expect(email.value).toBe('hello@world.io');
  });

  it('should throw for an invalid email', () => {
    expect(() => Email.create('not-an-email')).toThrow('Invalid email address');
  });

  it('should throw for an empty string', () => {
    expect(() => Email.create('')).toThrow('Invalid email address');
  });

  it('should consider two emails with the same value equal', () => {
    const a = Email.create('test@example.com');
    const b = Email.create('TEST@EXAMPLE.COM');
    expect(a.equals(b)).toBe(true);
  });
});
