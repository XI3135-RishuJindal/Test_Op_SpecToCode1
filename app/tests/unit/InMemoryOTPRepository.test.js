'use strict';

const InMemoryOTPRepository = require('../../../src/adapters/persistence/InMemoryOTPRepository');
const OTP = require('../../../src/domain/entities/OTP');

const makeOTP = (overrides = {}) =>
  new OTP({
    id: 'otp-1',
    userId: 'user-1',
    phoneNumber: '+15005550006',
    code: '123456',
    expiresAt: new Date(Date.now() + 300_000),
    ...overrides,
  });

describe('InMemoryOTPRepository', () => {
  let repo;

  beforeEach(() => {
    repo = new InMemoryOTPRepository();
  });

  it('should save and retrieve an OTP by id', async () => {
    const otp = makeOTP();
    await repo.save(otp);
    const found = await repo.findById('otp-1');
    expect(found).toBe(otp);
  });

  it('should return null for an unknown id', async () => {
    const found = await repo.findById('unknown');
    expect(found).toBeNull();
  });

  it('should find an active OTP by userId', async () => {
    const otp = makeOTP();
    await repo.save(otp);
    const found = await repo.findActiveByUserId('user-1');
    expect(found).toBe(otp);
  });

  it('should not return an expired OTP via findActiveByUserId', async () => {
    const otp = makeOTP({ expiresAt: new Date(Date.now() - 1000) });
    await repo.save(otp);
    const found = await repo.findActiveByUserId('user-1');
    expect(found).toBeNull();
  });

  it('should update an existing OTP', async () => {
    const otp = makeOTP();
    await repo.save(otp);
    otp.consume();
    await repo.update(otp);
    const found = await repo.findById('otp-1');
    expect(found.used).toBe(true);
  });

  it('should delete all OTPs for a user', async () => {
    await repo.save(makeOTP({ id: 'otp-1' }));
    await repo.save(makeOTP({ id: 'otp-2' }));
    await repo.deleteByUserId('user-1');
    expect(await repo.findById('otp-1')).toBeNull();
    expect(await repo.findById('otp-2')).toBeNull();
  });
});
