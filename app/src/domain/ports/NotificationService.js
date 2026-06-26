'use strict';

/**
 * Port: NotificationService
 *
 * Defines the contract for sending OTP codes to users.
 * Concrete adapters (Twilio, mock, etc.) must implement this interface.
 */
class NotificationService {
  /**
   * Send an OTP code to the specified phone number.
   * @param {string} phoneNumber - E.164 formatted phone number
   * @param {string} code        - The OTP code to send
   * @returns {Promise<{ messageId: string }>}
   */
  // eslint-disable-next-line no-unused-vars
  async sendOTP(phoneNumber, code) {
    throw new Error('NotificationService.sendOTP() must be implemented by an adapter.');
  }
}

module.exports = NotificationService;
