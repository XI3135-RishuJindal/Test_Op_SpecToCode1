import { VerificationToken } from '../../domain/entities/verification-token.entity';

const futureDate = (): Date => new Date(Date.now() + 60 * 60 * 1000);
const pastDate = (): Date => new Date(Date.now() - 1000);

describe('VerificationToken entity', () => {
  it('should be valid when not expired and not used', () => {
    const token = new VerificationToken({
      id: 'tok-1',
      userId: 'user-1',
      tokenHash: 'abc',
      expiresAt: futureDate(),
    });
    expect(token.isValid()).toBe(true);
  });

  it('should be invalid when expired', () => {
    const token = new VerificationToken({
      id: 'tok-2',
      userId: 'user-1',
      tokenHash: 'abc',
      expiresAt: pastDate(),
    });
    expect(token.isExpired()).toBe(true);
    expect(token.isValid()).toBe(false);
  });

  it('should be invalid after markUsed()', () => {
    const token = new VerificationToken({
      id: 'tok-3',
      userId: 'user-1',
      tokenHash: 'abc',
      expiresAt: futureDate(),
    });
    token.markUsed();
    expect(token.isUsed()).toBe(true);
    expect(token.isValid()).toBe(false);
  });

  it('should throw when markUsed() is called on an already-used token', () => {
    const token = new VerificationToken({
      id: 'tok-4',
      userId: 'user-1',
      tokenHash: 'abc',
      expiresAt: futureDate(),
      usedAt: new Date(),
    });
    expect(() => token.markUsed()).toThrow('already used or expired');
  });

  it('should throw when markUsed() is called on an expired token', () => {
    const token = new VerificationToken({
      id: 'tok-5',
      userId: 'user-1',
      tokenHash: 'abc',
      expiresAt: pastDate(),
    });
    expect(() => token.markUsed()).toThrow('already used or expired');
  });
});
