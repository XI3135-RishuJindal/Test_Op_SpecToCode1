'use strict';

const OTP = require('../../src/domain/entities/OTP');

describe('OTP Entity', () => {
  const makeOTP = (overrides = {}) =>
    new OTP({
      id: 'otp-1',
      userId: 'user-1',
      phoneNumber: '+15005550006',
      code: '123456',
      expiresAt: new Date(Date.now() + 300_000),
      ...overrides,
    });

  describe('isExpired()', () => {
    it('should return false when expiresAt is in the future', () => {
      const otp = makeOTP();
      expect(otp.isExpired()).toBe(false);
    });

    it('should return true when expiresAt is in the past', () => {
      const otp = makeOTP({ expiresAt: new Date(Date.now() - 1000) });
      expect(otp.isExpired()).toBe(true);
    });
  });

  describe('isValid()', () => {
    it('should return true for a fresh, unused OTP', () => {
      const otp = makeOTP();
      expect(otp.isValid()).toBe(true);
    });

    it('should return false for an expired OTP', () => {
      const otp = makeOTP({ expiresAt: new Date(Date.now() - 1000) });
      expect(otp.isValid()).toBe(false);
    });

    it('should return false for a used OTP', () => {
      const otp = makeOTP({ used: true });
      expect(otp.isValid()).toBe(false);
    });
  });

  describe('consume()', () => {
    it('should mark the OTP as used', () => {
      const otp = makeOTP();
      otp.consume();
      expect(otp.used).toBe(true);
    });

    it('should return the OTP instance for chaining', () => {
      const otp = makeOTP();
      expect(otp.consume()).toBe(otp);
    });
  });
});
