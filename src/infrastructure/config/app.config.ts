import { registerAs } from '@nestjs/config';

export default registerAs('app', () => ({
  port: parseInt(process.env.PORT ?? '3000', 10),
  nodeEnv: process.env.NODE_ENV ?? 'development',
  verificationTokenTtlMinutes: parseInt(
    process.env.VERIFICATION_TOKEN_TTL_MINUTES ?? '60',
    10,
  ),
}));
