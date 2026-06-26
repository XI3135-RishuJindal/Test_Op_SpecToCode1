'use strict';

const generateOTPFactory = require('../../../src/domain/usecases/generateOTP');
const validateOTPFactory = require('../../../src/domain/usecases/validateOTP');
const InMemoryOTPRepository = require('../../../src/adapters/persistence/InMemoryOTPRepository');
const MockNotificationService = require('../../../src/adapters/notifications/MockNotificationService');

describe('generateOTP use-case', () => {
  let otpRepository;
  let notificationService;
  let generateOTP;

  beforeEach(() => {
    otpRepository = new InMemoryOTPRepository();
    notificationService = new MockNotificationService();
    generateOTP = generateOTPFactory({ otpRepository, notificationService });
  });

  it('should return an otpId and expiresAt', async () => {
    const result = await generateOTP.execute({ userId: 'u1', phoneNumber: '+15005550006' });
    expect(result.otpId).toBeDefined();
    expect(result.expiresAt).toBeInstanceOf(Date);
  });

  it('should persist the OTP in the repository', async () => {
    const { otpId } = await generateOTP.execute({ userId: 'u1', phoneNumber: '+15005550006' });
    const saved = await otpRepository.findById(otpId);
    expect(saved).not.toBeNull();
    expect(saved.userId).toBe('u1');
  });

  it('should throw when userId is missing', async () => {
    await expect(generateOTP.execute({ phoneNumber: '+15005550006' })).rejects.toThrow('userId is required');
  });

  it('should throw when phoneNumber is missing', async () => {
    await expect(generateOTP.execute({ userId: 'u1' })).rejects.toThrow('phoneNumber is required');
  });
});

describe('validateOTP use-case', () => {
  let otpRepository;
  let notificationService;
  let generateOTP;
  let validateOTP;

  beforeEach(() => {
    otpRepository = new InMemoryOTPRepository();
    notificationService = new MockNotificationService();
    generateOTP = generateOTPFactory({ otpRepository, notificationService });
    validateOTP = validateOTPFactory({ otpRepository });
  });

  it('should return valid: true for a correct code', async () => {
    const { otpId } = await generateOTP.execute({ userId: 'u2', phoneNumber: '+15005550006' });
    const otp = await otpRepository.findById(otpId);
    const result = await validateOTP.execute({ userId: 'u2', code: otp.code });
    expect(result.valid).toBe(true);
  });

  it('should return valid: false for an incorrect code', async () => {
    await generateOTP.execute({ userId: 'u3', phoneNumber: '+15005550006' });
    const result = await validateOTP.execute({ userId: 'u3', code: '000000' });
    expect(result.valid).toBe(false);
  });

  it('should mark the OTP as used after successful validation', async () => {
    const { otpId } = await generateOTP.execute({ userId: 'u4', phoneNumber: '+15005550006' });
    const otp = await otpRepository.findById(otpId);
    await validateOTP.execute({ userId: 'u4', code: otp.code });
    const updated = await otpRepository.findById(otpId);
    expect(updated.used).toBe(true);
  });

  it('should return valid: false when no active OTP exists', async () => {
    const result = await validateOTP.execute({ userId: 'u-none', code: '123456' });
    expect(result.valid).toBe(false);
  });
});
