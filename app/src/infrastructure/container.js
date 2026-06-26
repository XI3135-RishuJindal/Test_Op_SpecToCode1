'use strict';

/**
 * Dependency Injection Container
 *
 * Wires together domain use-cases with their concrete adapters.
 * Swap adapters here without touching domain logic.
 */

const InMemoryOTPRepository = require('../adapters/persistence/InMemoryOTPRepository');
const MockNotificationService = require('../adapters/notifications/MockNotificationService');

const generateOTPFactory = require('../domain/usecases/generateOTP');
const validateOTPFactory = require('../domain/usecases/validateOTP');

// ── Adapter selection ─────────────────────────────────────────────────────────
const otpRepository = new InMemoryOTPRepository();

let notificationService;
if (process.env.NODE_ENV === 'production' || process.env.USE_TWILIO === 'true') {
  // Lazy-load Twilio adapter only when needed to avoid env-var validation in dev/test
  const TwilioNotificationService = require('../adapters/notifications/TwilioNotificationService');
  notificationService = new TwilioNotificationService();
} else {
  notificationService = new MockNotificationService();
}

// ── Use-case instances ────────────────────────────────────────────────────────
const generateOTP = generateOTPFactory({ otpRepository, notificationService });
const validateOTP = validateOTPFactory({ otpRepository });

// ── Simple service locator ────────────────────────────────────────────────────
const services = {
  otpRepository,
  notificationService,
  generateOTP,
  validateOTP,
};

const container = {
  /**
   * @param {string} name
   * @returns {*}
   */
  resolve(name) {
    if (!services[name]) {
      throw new Error(`Service "${name}" is not registered in the container.`);
    }
    return services[name];
  },
};

module.exports = container;
