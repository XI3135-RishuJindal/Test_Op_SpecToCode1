'use strict';

/**
 * Use-case: Validate a submitted OTP code.
 *
 * @param {object} deps
 * @param {import('../ports/OTPRepository')} deps.otpRepository
 */
const validateOTPFactory = ({ otpRepository }) => {
  /**
   * @param {object} params
   * @param {string} params.userId - The user submitting the OTP
   * @param {string} params.code   - The code entered by the user
   * @returns {Promise<{ valid: boolean, reason?: string }>}
   */
  const execute = async ({ userId, code }) => {
    if (!userId) throw new Error('userId is required');
    if (!code) throw new Error('code is required');

    const otp = await otpRepository.findActiveByUserId(userId);

    if (!otp) {
      return { valid: false, reason: 'No active OTP found for this user.' };
    }

    if (otp.isExpired()) {
      return { valid: false, reason: 'OTP has expired.' };
    }

    if (otp.used) {
      return { valid: false, reason: 'OTP has already been used.' };
    }

    if (otp.code !== code) {
      return { valid: false, reason: 'Invalid OTP code.' };
    }

    otp.consume();
    await otpRepository.update(otp);

    return { valid: true };
  };

  return { execute };
};

module.exports = validateOTPFactory;
