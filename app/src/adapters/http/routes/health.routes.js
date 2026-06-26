'use strict';

const express = require('express');

const router = express.Router();

/**
 * GET /health
 * Returns service liveness status.
 *
 * @returns {{ status: string, service: string, timestamp: string }}
 */
router.get('/', (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: 'multi-factor-authentication-service',
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
