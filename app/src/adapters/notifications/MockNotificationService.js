'use strict';

const NotificationService = require('../../domain/ports/NotificationService');
const logger = require('../../infrastructure/logger');

/**
 * Mock adapter for NotificationService.
 * Logs OTP codes instead of sending real SMS messages.
 * Use in development / testing environments.
 */
class MockNotificationService extends NotificationService {
  /**
   * @param {string} phoneNumber
   * @param {string} code
   * @returns {Promise<{ messageId: string }>}
   */
  async sendOTP(phoneNumber, code) {
    const messageId = `mock-${Date.now()}`;
    logger.info(`[MockNotificationService] OTP ${code} would be sent to ${phoneNumber} (messageId=${messageId})`);
    return { messageId };
  }
}

module.exports = MockNotificationService;
