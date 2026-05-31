import { createApp } from './app';
import { createServer } from 'http';
import { connectRedis, disconnectRedis } from './infrastructure/redis.client';
import { initSchema, disconnectPostgres } from './infrastructure/postgres.client';
import { disconnectKafka } from './infrastructure/kafka.client';
import { initTracing, shutdownTracing } from './infrastructure/tracing';
import { WebSocketUpgradeHandler } from './websocket/ws-upgrade.handler';
import { AuthService } from './services/auth.service';
import { RateLimiterService } from './services/rate-limiter.service';
import { AuditService } from './services/audit.service';
import { config } from './config';
import { logger } from './infrastructure/logger';

async function bootstrap(): Promise<void> {
  // Initialize tracing first (before any instrumented code)
  initTracing();

  // Connect to infrastructure
  logger.info('Connecting to Redis...');
  await connectRedis();

  logger.info('Initializing database schema...');
  await initSchema();

  // Create Express app
  const app = createApp();
  const server = createServer(app);

  // Attach WebSocket upgrade handler
  const authService = new AuthService();
  const rateLimiterService = new RateLimiterService();
  const auditService = new AuditService();
  const wsHandler = new WebSocketUpgradeHandler(authService, rateLimiterService, auditService);
  wsHandler.attach(server);

  // Start listening
  server.listen(config.port, () => {
    logger.info(
      {
        port: config.port,
        env: config.env,
        version: config.service.version,
      },
      `API Gateway Service started on port ${config.port}`,
    );
  });

  // Graceful shutdown
  const shutdown = async (signal: string): Promise<void> => {
    logger.info({ signal }, 'Shutdown signal received');

    server.close(async () => {
      logger.info('HTTP server closed');
      try {
        await Promise.all([
          disconnectRedis(),
          disconnectPostgres(),
          disconnectKafka(),
          shutdownTracing(),
        ]);
        logger.info('All connections closed — exiting');
        process.exit(0);
      } catch (err) {
        logger.error({ err }, 'Error during shutdown');
        process.exit(1);
      }
    });

    // Force exit after 30s
    setTimeout(() => {
      logger.error('Forced shutdown after timeout');
      process.exit(1);
    }, 30_000);
  };

  process.on('SIGTERM', () => void shutdown('SIGTERM'));
  process.on('SIGINT', () => void shutdown('SIGINT'));

  process.on('unhandledRejection', (reason) => {
    logger.error({ reason }, 'Unhandled promise rejection');
  });

  process.on('uncaughtException', (err) => {
    logger.fatal({ err }, 'Uncaught exception — shutting down');
    void shutdown('uncaughtException');
  });
}

bootstrap().catch((err) => {
  // eslint-disable-next-line no-console
  console.error('Bootstrap failed:', err);
  process.exit(1);
});
