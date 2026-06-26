'use strict';

const NotificationService = require('../../domain/ports/NotificationService');
const logger = require('../../infrastructure/logger');

/**
 * Twilio adapter for NotificationService.
 * Sends OTP codes via Twilio Verify or SMS.
 */
class TwilioNotificationService extends NotificationService {
  constructor() {
    super();

    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;

    if (!accountSid || !authToken) {
      throw new Error('TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set.');
    }

    // Lazy-require so tests can mock without a real Twilio client
    const twilio = require('twilio');
    this._client = twilio(accountSid, authToken);
    this._from = process.env.TWILIO_PHONE_NUMBER;
  }

  /**
   * @param {string} phoneNumber - E.164 formatted destination number
   * @param {string} code        - OTP code to send
   * @returns {Promise<{ messageId: string }>}
   */
  async sendOTP(phoneNumber, code) {
    const message = await this._client.messages.create({
      body: `Your verification code is: ${code}. It expires in ${process.env.OTP_TTL_SECONDS || 300} seconds.`,
      from: this._from,
      to: phoneNumber,
    });

    logger.info(`OTP sent to ${phoneNumber}, messageSid=${message.sid}`);
    return { messageId: message.sid };
  }
}

module.exports = TwilioNotificationService;
