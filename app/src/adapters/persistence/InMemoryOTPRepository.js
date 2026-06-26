'use strict';

const OTPRepository = require('../../domain/ports/OTPRepository');
const OTP = require('../../domain/entities/OTP');

/**
 * In-memory adapter for OTPRepository.
 * Suitable for development and testing; replace with a persistent adapter in production.
 */
class InMemoryOTPRepository extends OTPRepository {
  constructor() {
    super();
    /** @type {Map<string, OTP>} */
    this._store = new Map();
  }

  /**
   * @param {OTP} otp
   * @returns {Promise<OTP>}
   */
  async save(otp) {
    this._store.set(otp.id, otp);
    return otp;
  }

  /**
   * @param {string} id
   * @returns {Promise<OTP|null>}
   */
  async findById(id) {
    return this._store.get(id) || null;
  }

  /**
   * @param {string} userId
   * @returns {Promise<OTP|null>}
   */
  async findActiveByUserId(userId) {
    for (const otp of this._store.values()) {
      if (otp.userId === userId && otp.isValid()) {
        return otp;
      }
    }
    return null;
  }

  /**
   * @param {OTP} otp
   * @returns {Promise<OTP>}
   */
  async update(otp) {
    if (!this._store.has(otp.id)) {
      throw new Error(`OTP with id ${otp.id} not found.`);
    }
    this._store.set(otp.id, otp);
    return otp;
  }

  /**
   * @param {string} userId
   * @returns {Promise<void>}
   */
  async deleteByUserId(userId) {
    for (const [id, otp] of this._store.entries()) {
      if (otp.userId === userId) {
        this._store.delete(id);
      }
    }
  }
}

module.exports = InMemoryOTPRepository;
