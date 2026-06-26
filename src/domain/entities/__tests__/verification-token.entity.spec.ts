import { VerificationToken } from '../verification-token.entity';

describe('VerificationToken aggregate', () => {
  const futureDate = new Date(Date.now() + 60 * 60 * 1000); // 1 hour from now
  const pastDate = new Date(Date.now() - 60 * 60 * 1000);   // 1 hour ago

  it('is not expired when expiresAt is in the future', () => {
    const token = VerificationToken.create({
      id: 'tok-1',
      userId: 'user-1',
      tokenHash: 'abc123',
      expiresAt: futureDate,
    });
    expect(token.isExpired()).toBe(false);
  });

  it('is expired when expiresAt is in the past', () => {
    const token = VerificationToken.create({
      id: 'tok-2',
      userId: 'user-1',
      tokenHash: 'abc123',
      expiresAt: pastDate,
    });
    expect(token.isExpired()).toBe(true);
  });

  it('marks token as used', () => {
    const token = VerificationToken.create({
      id: 'tok-3',
      userId: 'user-1',
      tokenHash: 'abc123',
      expiresAt: futureDate,
    });
    expect(token.isUsed()).toBe(false);
    token.markUsed();
    expect(token.isUsed()).toBe(true);
  });

  it('throws when marking an already-used token', () => {
    const token = VerificationToken.create({
      id: 'tok-4',
      userId: 'user-1',
      tokenHash: 'abc123',
      expiresAt: futureDate,
    });
    token.markUsed();
    expect(() => token.markUsed()).toThrow(/already used/);
  });

  it('throws when marking an expired token as used', () => {
    const token = VerificationToken.create({
      id: 'tok-5',
      userId: 'user-1',
      tokenHash: 'abc123',
      expiresAt: pastDate,
    });
    expect(() => token.markUsed()).toThrow(/expired/);
  });
});
