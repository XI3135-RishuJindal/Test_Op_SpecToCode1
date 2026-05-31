import { IncomingMessage, Server } from 'http';
import { Socket } from 'net';
import WebSocket, { WebSocketServer } from 'ws';
import { URL } from 'url';
import { AuthService } from '../services/auth.service';
import { RateLimiterService } from '../services/rate-limiter.service';
import { AuditService } from '../services/audit.service';
import { config } from '../config';
import { logger } from '../infrastructure/logger';
import { activeWebSocketConnections } from '../infrastructure/metrics';
import { v4 as uuidv4 } from 'uuid';

const MAX_WS_CONNECTIONS_PER_USER = 5;

export class WebSocketUpgradeHandler {
  private readonly wss: WebSocketServer;
  private readonly connectionCount = new Map<string, number>();

  constructor(
    private readonly authService: AuthService,
    private readonly rateLimiter: RateLimiterService,
    private readonly auditService: AuditService,
  ) {
    this.wss = new WebSocketServer({ noServer: true });
  }

  /**
   * Attach the WS upgrade handler to an HTTP server.
   */
  attach(server: Server): void {
    server.on('upgrade', async (req: IncomingMessage, socket: Socket, head: Buffer) => {
      try {
        await this.handleUpgrade(req, socket, head);
      } catch (err) {
        logger.error({ err }, 'WebSocket upgrade error');
        socket.write('HTTP/1.1 500 Internal Server Error\r\n\r\n');
        socket.destroy();
      }
    });
  }

  private async handleUpgrade(
    req: IncomingMessage,
    socket: Socket,
    head: Buffer,
  ): Promise<void> {
    // Only handle /ws/v1/notifications
    const url = new URL(req.url ?? '/', `http://${req.headers.host}`);
    if (url.pathname !== '/ws/v1/notifications') {
      socket.write('HTTP/1.1 404 Not Found\r\n\r\n');
      socket.destroy();
      return;
    }

    const requestId = uuidv4();

    // Extract JWT from Authorization header or ?token query param
    const authHeader = req.headers['authorization'] as string | undefined;
    const tokenParam = url.searchParams.get('token');
    const rawToken = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : tokenParam;

    if (!rawToken) {
      logger.warn({ requestId }, 'WS upgrade rejected: missing token');
      socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
      socket.destroy();
      return;
    }

    // Validate JWT
    const authContext = await this.authService.verifyJwt(rawToken);
    if (!authContext) {
      logger.warn({ requestId }, 'WS upgrade rejected: invalid token');
      socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
      socket.destroy();
      return;
    }

    // Rate limit: connection count per user
    const userConnections = this.connectionCount.get(authContext.userId) ?? 0;
    if (userConnections >= MAX_WS_CONNECTIONS_PER_USER) {
      const rateLimitResult = await this.rateLimiter.consume(
        `ws:${authContext.userId}`,
        60_000,
        MAX_WS_CONNECTIONS_PER_USER,
      );

      if (!rateLimitResult.allowed) {
        logger.warn({ userId: authContext.userId }, 'WS upgrade rejected: connection limit exceeded');
        socket.write('HTTP/1.1 429 Too Many Requests\r\n\r\n');
        socket.destroy();
        return;
      }
    }

    // Upgrade the connection
    this.wss.handleUpgrade(req, socket, head, (ws) => {
      this.wss.emit('connection', ws, req, authContext, requestId);
      this.handleConnection(ws, authContext.userId, authContext, requestId, rawToken);
    });
  }

  private handleConnection(
    clientWs: WebSocket,
    userId: string,
    authContext: { userId: string; email: string },
    requestId: string,
    token: string,
  ): void {
    // Track connection count
    const current = this.connectionCount.get(userId) ?? 0;
    this.connectionCount.set(userId, current + 1);
    activeWebSocketConnections.inc();

    logger.info({ userId, requestId }, 'WebSocket connection established');

    // Connect to upstream notification service
    const upstreamUrl = `${config.upstreams.notification.replace('http', 'ws')}/ws/v1/notifications?token=${token}`;
    const upstreamWs = new WebSocket(upstreamUrl, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Request-ID': requestId,
        'X-User-ID': userId,
      },
    });

    // Audit event
    void this.auditService.log({
      principal: userId,
      action: 'WS_CONNECTED',
      resource: '/ws/v1/notifications',
      status: 'success',
      correlationId: requestId,
      path: '/ws/v1/notifications',
    });

    // Forward upstream → client
    upstreamWs.on('message', (data) => {
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.send(data);
      }
    });

    // Forward client → upstream
    clientWs.on('message', (data) => {
      if (upstreamWs.readyState === WebSocket.OPEN) {
        try {
          const event = JSON.parse(data.toString()) as { type: string };

          // Handle ping locally
          if (event.type === 'ping') {
            clientWs.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
            return;
          }

          upstreamWs.send(data);
        } catch {
          upstreamWs.send(data);
        }
      }
    });

    // Handle client disconnect
    clientWs.on('close', (code) => {
      logger.info({ userId, requestId, code }, 'WebSocket client disconnected');
      this.decrementConnectionCount(userId);
      activeWebSocketConnections.dec();

      if (upstreamWs.readyState === WebSocket.OPEN) {
        upstreamWs.close();
      }
    });

    // Handle upstream disconnect
    upstreamWs.on('close', (code) => {
      logger.info({ userId, requestId, code }, 'WebSocket upstream disconnected');
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.close(code);
      }
    });

    // Handle errors
    clientWs.on('error', (err) => {
      logger.error({ err, userId, requestId }, 'WebSocket client error');
      this.decrementConnectionCount(userId);
      activeWebSocketConnections.dec();
    });

    upstreamWs.on('error', (err) => {
      logger.error({ err, userId, requestId }, 'WebSocket upstream error');
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.close(1011, 'Upstream error');
      }
    });

    // On upstream open, forward connection.ack if upstream sends it
    upstreamWs.on('open', () => {
      logger.debug({ userId, requestId }, 'WebSocket upstream connected');
    });
  }

  private decrementConnectionCount(userId: string): void {
    const current = this.connectionCount.get(userId) ?? 1;
    const next = current - 1;
    if (next <= 0) {
      this.connectionCount.delete(userId);
    } else {
      this.connectionCount.set(userId, next);
    }
  }
}
