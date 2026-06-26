'use strict';

const { v4: uuidv4 } = require('uuid');
const OTP = require('../entities/OTP');

/**
 * Use-case: Generate and send a new OTP for a user.
 *
 * @param {object} deps
 * @param {import('../ports/OTPRepository')}    deps.otpRepository
 * @param {import('../ports/NotificationService')} deps.notificationService
 */
const generateOTPFactory = ({ otpRepository, notificationService }) => {
  /**
   * @param {object} params
   * @param {string} params.userId      - The user requesting an OTP
   * @param {string} params.phoneNumber - Destination phone number (E.164)
   * @returns {Promise<{ otpId: string, expiresAt: Date }>}
   */
  const execute = async ({ userId, phoneNumber }) => {
    if (!userId) throw new Error('userId is required');
    if (!phoneNumber) throw new Error('phoneNumber is required');

    // Invalidate any existing active OTPs for this user
    await otpRepository.deleteByUserId(userId);

    // Generate a 6-digit code
    const code = String(Math.floor(100000 + Math.random() * 900000));

    const ttlMs = parseInt(process.env.OTP_TTL_SECONDS || '300', 10) * 1000;
    const expiresAt = new Date(Date.now() + ttlMs);

    const otp = new OTP({
      id: uuidv4(),
      userId,
      phoneNumber,
      code,
      expiresAt,
    });

    await otpRepository.save(otp);
    await notificationService.sendOTP(phoneNumber, code);

    return { otpId: otp.id, expiresAt };
  };

  return { execute };
};

module.exports = generateOTPFactory;
