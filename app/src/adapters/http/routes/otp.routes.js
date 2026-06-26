'use strict';

const express = require('express');
const container = require('../../../infrastructure/container');

const router = express.Router();

/**
 * POST /api/v1/otp/generate
 * Generate and send a new OTP to the user's phone number.
 *
 * Body: { userId: string, phoneNumber: string }
 * Response 201: { otpId: string, expiresAt: string }
 */
router.post('/generate', async (req, res, next) => {
  try {
    const { userId, phoneNumber } = req.body;

    if (!userId || !phoneNumber) {
      return res.status(400).json({ error: 'userId and phoneNumber are required.' });
    }

    const generateOTP = container.resolve('generateOTP');
    const result = await generateOTP.execute({ userId, phoneNumber });

    return res.status(201).json({
      otpId: result.otpId,
      expiresAt: result.expiresAt.toISOString(),
    });
  } catch (err) {
    return next(err);
  }
});

/**
 * POST /api/v1/otp/validate
 * Validate a submitted OTP code.
 *
 * Body: { userId: string, code: string }
 * Response 200: { valid: boolean, reason?: string }
 */
router.post('/validate', async (req, res, next) => {
  try {
    const { userId, code } = req.body;

    if (!userId || !code) {
      return res.status(400).json({ error: 'userId and code are required.' });
    }

    const validateOTP = container.resolve('validateOTP');
    const result = await validateOTP.execute({ userId, code });

    return res.status(200).json(result);
  } catch (err) {
    return next(err);
  }
});

module.exports = router;
