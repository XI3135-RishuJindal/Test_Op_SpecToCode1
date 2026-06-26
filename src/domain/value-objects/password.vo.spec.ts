import { Password } from '../../domain/value-objects/password.vo';

describe('Password value object', () => {
  const validPassword = 'Str0ng!Pass';

  it('should not throw for a valid password', () => {
    expect(() => Password.validate(validPassword)).not.toThrow();
  });

  it('should throw when password is too short', () => {
    expect(() => Password.validate('Ab1!')).toThrow('at least 8 characters');
  });

  it('should throw when password exceeds max length', () => {
    const tooLong = 'A'.repeat(129) + '1!a';
    expect(() => Password.validate(tooLong)).toThrow('not exceed 128 characters');
  });

  it('should throw when no uppercase letter', () => {
    expect(() => Password.validate('str0ng!pass')).toThrow('uppercase');
  });

  it('should throw when no lowercase letter', () => {
    expect(() => Password.validate('STR0NG!PASS')).toThrow('lowercase');
  });

  it('should throw when no digit', () => {
    expect(() => Password.validate('Strong!Pass')).toThrow('digit');
  });

  it('should throw when no special character', () => {
    expect(() => Password.validate('Str0ngPass')).toThrow('special character');
  });
});
