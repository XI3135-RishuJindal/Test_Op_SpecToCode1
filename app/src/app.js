'use strict';

require('dotenv').config();

const express = require('express');
const healthRouter = require('./adapters/http/routes/health.routes');
const otpRouter = require('./adapters/http/routes/otp.routes');
const errorHandler = require('./adapters/http/middleware/errorHandler');
const requestLogger = require('./adapters/http/middleware/requestLogger');

const app = express();

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(requestLogger);

// ── Routes ────────────────────────────────────────────────────────────────────
app.use('/health', healthRouter);
app.use('/api/v1/otp', otpRouter);

// ── Error handling ────────────────────────────────────────────────────────────
app.use(errorHandler);

module.exports = app;
