'use strict';

/**
 * OTP Domain Entity
 *
 * Represents a one-time password record in the system.
 */
class OTP {
  /**
   * @param {object} params
   * @param {string} params.id          - Unique identifier for this OTP record
   * @param {string} params.userId      - The user this OTP belongs to
   * @param {string} params.phoneNumber - Destination phone number
   * @param {string} params.code        - The OTP code (hashed or plain depending on adapter)
   * @param {Date}   params.expiresAt   - Expiry timestamp
   * @param {boolean} params.used       - Whether the OTP has been consumed
   * @param {Date}   params.createdAt   - Creation timestamp
   */
  constructor({ id, userId, phoneNumber, code, expiresAt, used = false, createdAt = new Date() }) {
    this.id = id;
    this.userId = userId;
    this.phoneNumber = phoneNumber;
    this.code = code;
    this.expiresAt = expiresAt;
    this.used = used;
    this.createdAt = createdAt;
  }

  /**
   * Returns true if the OTP has expired.
   * @returns {boolean}
   */
  isExpired() {
    return new Date() > this.expiresAt;
  }

  /**
   * Returns true if the OTP is still valid (not expired and not used).
   * @returns {boolean}
   */
  isValid() {
    return !this.used && !this.isExpired();
  }

  /**
   * Marks the OTP as used.
   * @returns {OTP}
   */
  consume() {
    this.used = true;
    return this;
  }
}

module.exports = OTP;
