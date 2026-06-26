import { Password } from '../password.vo';

describe('Password value object', () => {
  const validPassword = 'Str0ng!Pass';

  it('accepts a valid password', () => {
    expect(() => new Password(validPassword)).not.toThrow();
  });

  it('rejects passwords shorter than 8 characters', () => {
    expect(() => new Password('Ab1!')).toThrow(/minimum length/);
  });

  it('rejects passwords without uppercase', () => {
    expect(() => new Password('str0ng!pass')).toThrow(/uppercase/);
  });

  it('rejects passwords without lowercase', () => {
    expect(() => new Password('STR0NG!PASS')).toThrow(/lowercase/);
  });

  it('rejects passwords without a digit', () => {
    expect(() => new Password('Strong!Pass')).toThrow(/digit/);
  });

  it('rejects passwords without a special character', () => {
    expect(() => new Password('Str0ngPass')).toThrow(/special/);
  });

  it('rejects passwords exceeding 128 characters', () => {
    const long = 'Aa1!' + 'x'.repeat(125);
    expect(() => new Password(long)).toThrow(/maximum length/);
  });
});
