'use strict';

/**
 * Port: OTPRepository
 *
 * Defines the persistence contract for OTP records.
 * Concrete adapters (in-memory, Redis, SQL, etc.) must implement this interface.
 */
class OTPRepository {
  /**
   * Persist a new OTP record.
   * @param {import('../entities/OTP')} otp
   * @returns {Promise<import('../entities/OTP')>}
   */
  // eslint-disable-next-line no-unused-vars
  async save(otp) {
    throw new Error('OTPRepository.save() must be implemented by an adapter.');
  }

  /**
   * Find an OTP record by its unique ID.
   * @param {string} id
   * @returns {Promise<import('../entities/OTP')|null>}
   */
  // eslint-disable-next-line no-unused-vars
  async findById(id) {
    throw new Error('OTPRepository.findById() must be implemented by an adapter.');
  }

  /**
   * Find the most recent unused, non-expired OTP for a given user.
   * @param {string} userId
   * @returns {Promise<import('../entities/OTP')|null>}
   */
  // eslint-disable-next-line no-unused-vars
  async findActiveByUserId(userId) {
    throw new Error('OTPRepository.findActiveByUserId() must be implemented by an adapter.');
  }

  /**
   * Persist changes to an existing OTP record.
   * @param {import('../entities/OTP')} otp
   * @returns {Promise<import('../entities/OTP')>}
   */
  // eslint-disable-next-line no-unused-vars
  async update(otp) {
    throw new Error('OTPRepository.update() must be implemented by an adapter.');
  }

  /**
   * Delete all OTP records for a given user.
   * @param {string} userId
   * @returns {Promise<void>}
   */
  // eslint-disable-next-line no-unused-vars
  async deleteByUserId(userId) {
    throw new Error('OTPRepository.deleteByUserId() must be implemented by an adapter.');
  }
}

module.exports = OTPRepository;
