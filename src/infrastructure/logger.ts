import pino from 'pino';
import { config } from '../config';

// PII field names to mask in logs
const PII_FIELDS = ['password', 'token', 'accessToken', 'refreshToken', 'mfaSessionToken',
  'authorization', 'x-api-key', 'otpCode', 'phoneNumber', 'email', 'cardNumber', 'cvv', 'pan'];

function redactPaths(): string[] {
  return [
    'req.headers.authorization',
    'req.headers["x-api-key"]',
    'req.body.password',
    'req.body.otpCode',
    'req.body.refreshToken',
    'req.body.accessToken',
    'res.body.accessToken',
    'res.body.refreshToken',
    'res.body.mfaSessionToken',
    ...PII_FIELDS.map((f) => `*.${f}`),
  ];
}

export const logger = pino({
  level: config.observability.logLevel,
  redact: {
    paths: redactPaths(),
    censor: '[REDACTED]',
  },
  formatters: {
    level(label) {
      return { level: label };
    },
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  base: {
    service: config.service.name,
    version: config.service.version,
    env: config.env,
  },
});

export type Logger = typeof logger;
