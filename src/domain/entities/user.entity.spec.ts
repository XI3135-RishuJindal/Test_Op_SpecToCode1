import { User } from '../../domain/entities/user.entity';
import { AccountStatus } from '../../domain/enums/account-status.enum';

const makeUser = (status: AccountStatus = AccountStatus.PENDING_VERIFICATION): User =>
  new User({
    id: 'test-id',
    email: 'user@example.com',
    passwordHash: 'hashed',
    status,
    createdAt: new Date(),
    updatedAt: new Date(),
  });

describe('User aggregate', () => {
  it('should expose its properties', () => {
    const user = makeUser();
    expect(user.id).toBe('test-id');
    expect(user.email).toBe('user@example.com');
    expect(user.status).toBe(AccountStatus.PENDING_VERIFICATION);
  });

  it('should activate a PENDING_VERIFICATION account', () => {
    const user = makeUser();
    user.activate();
    expect(user.status).toBe(AccountStatus.ACTIVE);
    expect(user.isActive()).toBe(true);
  });

  it('should throw when activating an already ACTIVE account', () => {
    const user = makeUser(AccountStatus.ACTIVE);
    expect(() => user.activate()).toThrow('Cannot activate account');
  });

  it('isPendingVerification should return true for PENDING_VERIFICATION', () => {
    const user = makeUser();
    expect(user.isPendingVerification()).toBe(true);
  });

  it('isActive should return false for PENDING_VERIFICATION', () => {
    const user = makeUser();
    expect(user.isActive()).toBe(false);
  });
});
