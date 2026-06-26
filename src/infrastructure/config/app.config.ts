import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  port: parseInt(process.env.PORT ?? '3000', 10),
  nodeEnv: process.env.NODE_ENV ?? 'development',
  jwtSecret: process.env.JWT_SECRET ?? 'change-me-in-production',
  tokenTtlMinutes: parseInt(process.env.VERIFICATION_TOKEN_TTL_MINUTES ?? '60', 10),
}));
