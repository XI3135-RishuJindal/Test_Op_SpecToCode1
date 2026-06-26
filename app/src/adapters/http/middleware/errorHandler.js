'use strict';

const logger = require('../../../infrastructure/logger');

/**
 * Global error-handling middleware.
 * Must be registered last in the Express middleware chain.
 *
 * @param {Error}              err
 * @param {import('express').Request}  req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
// eslint-disable-next-line no-unused-vars
const errorHandler = (err, req, res, next) => {
  logger.error(`Unhandled error: ${err.message}`, { stack: err.stack });

  const statusCode = err.statusCode || 500;
  const message = statusCode === 500 ? 'Internal Server Error' : err.message;

  res.status(statusCode).json({ error: message });
};

module.exports = errorHandler;
