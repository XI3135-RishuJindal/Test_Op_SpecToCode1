import { User } from '../user.entity';
import { Email } from '../../value-objects/email.vo';
import { AccountStatus } from '../../enums/account-status.enum';

describe('User aggregate', () => {
  const buildUser = (status = AccountStatus.PENDING_VERIFICATION): User =>
    User.create({
      id: 'user-1',
      email: new Email('alice@example.com'),
      passwordHash: '$argon2id$...',
      status,
      idempotencyKey: 'idem-key-1',
    });

  it('creates a user with PENDING_VERIFICATION status', () => {
    const user = buildUser();
    expect(user.status).toBe(AccountStatus.PENDING_VERIFICATION);
  });

  it('activates a PENDING_VERIFICATION user', () => {
    const user = buildUser();
    user.activate();
    expect(user.status).toBe(AccountStatus.ACTIVE);
  });

  it('throws when activating a non-pending user', () => {
    const user = buildUser(AccountStatus.ACTIVE);
    expect(() => user.activate()).toThrow();
  });

  it('suspends an active user', () => {
    const user = buildUser(AccountStatus.ACTIVE);
    user.suspend();
    expect(user.status).toBe(AccountStatus.SUSPENDED);
  });

  it('throws when suspending a deactivated user', () => {
    const user = buildUser(AccountStatus.DEACTIVATED);
    expect(() => user.suspend()).toThrow();
  });
});
