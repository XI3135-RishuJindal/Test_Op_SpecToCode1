// ============================================================
// Core domain types for API Gateway Service (SVC-001)
// ============================================================

// ---- Error / Response shapes ----

export interface ErrorResponse {
  error: string;       // machine-readable code
  message: string;
  statusCode: number;
  timestamp: string;
  requestId: string;
  path: string;
  details?: ErrorDetail[];
}

export interface ErrorDetail {
  field?: string;
  message: string;
  code?: string;
}

// ---- Auth / JWT ----

export interface AuthContext {
  userId: string;
  email: string;
  roles: string[];
  scopes: string[];
  mfaSatisfied: boolean;
  sessionId?: string;
  sub: string;
  iss: string;
  aud: string | string[];
  exp: number;
  iat: number;
}

export interface LoginRequest {
  username: string;
  password: string;
  deviceFingerprint?: string;
}

export interface LoginResponse {
  mfaSessionToken: string;
  mfaMethod: MfaMethod;
  maskedDestination: string;
  expiresIn: number; // seconds (300)
}

export type MfaMethod = 'totp' | 'sms' | 'email';

export interface MfaVerifyRequest {
  otpCode: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: 'Bearer';
  expiresIn: number;
}

export interface TokenRefreshRequest {
  refreshToken: string;
}

export interface LogoutRequest {
  accessToken?: string;
  refreshToken?: string;
}

export interface MfaEnrollRequest {
  method: MfaMethod;
  phoneNumber?: string;
  email?: string;
}

export interface MfaEnrollResponse {
  methodId: string;
  method: MfaMethod;
  status: 'pending' | 'active';
  qrCodeUri?: string; // TOTP only
}

// ---- User Profiles (F-01) ----

export interface CreateUserRequest {
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  privacySettings?: PrivacySettings;
}

export interface UpdateUserRequest {
  firstName?: string;
  lastName?: string;
  phoneNumber?: string;
  privacySettings?: PrivacySettings;
}

export interface UserResponse {
  userId: string;
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  privacySettings?: PrivacySettings;
  createdAt: string;
  updatedAt: string;
}

export interface PrivacySettings {
  shareEmail: boolean;
  sharePhone: boolean;
}

// ---- Reporting (F-03) ----

export type ReportStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ReportFormat = 'pdf' | 'csv';

export interface CreateReportRequest {
  name: string;
  type: string;
  format: ReportFormat;
  parameters?: Record<string, unknown>;
}

export interface UpdateReportRequest {
  name?: string;
  parameters?: Record<string, unknown>;
}

export interface ReportScheduleRequest {
  cronExpression: string;
  timezone?: string;
  enabled: boolean;
}

export interface ReportResponse {
  reportId: string;
  name: string;
  type: string;
  format: ReportFormat;
  status: ReportStatus;
  parameters?: Record<string, unknown>;
  schedule?: ReportScheduleRequest;
  createdAt: string;
  updatedAt: string;
  downloadUrl?: string;
}

// ---- Payments (F-04) ----

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';
export type Currency = string; // ISO 4217

export interface PaymentMethod {
  tokenId: string; // PCI-DSS: tokenized only
  type: 'card' | 'bank_transfer' | 'wallet';
}

export interface CreatePaymentRequest {
  amount: number;
  currency: Currency;
  paymentMethod: PaymentMethod;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface PaymentResponse {
  paymentId: string;
  amount: number;
  currency: Currency;
  status: PaymentStatus;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface RefundRequest {
  amount?: number; // partial refund if provided
  reason?: string;
}

export interface RefundResponse {
  refundId: string;
  paymentId: string;
  amount: number;
  status: string;
  createdAt: string;
}

// ---- Notifications (F-05) ----

export type NotificationType = 'info' | 'warning' | 'error' | 'success';

export interface NotificationResponse {
  notificationId: string;
  userId: string;
  type: NotificationType;
  title: string;
  body: string;
  read: boolean;
  createdAt: string;
}

export interface NotificationPreferences {
  channels: NotificationChannel[];
  types: NotificationType[];
}

export type NotificationChannel = 'email' | 'sms' | 'push' | 'in_app';

// ---- Pagination ----

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

// ---- Gateway Administration ----

export interface GatewayRoute {
  routeId: string;
  pathPattern: string;
  method: string | string[];
  upstreamUrl: string;
  authRequired: boolean;
  requiredScopes?: string[];
  stripPrefix?: string;
  addPrefix?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateGatewayRouteRequest {
  pathPattern: string;
  method: string | string[];
  upstreamUrl: string;
  authRequired?: boolean;
  requiredScopes?: string[];
  stripPrefix?: string;
  addPrefix?: string;
}

export interface RateLimitPolicy {
  policyId: string;
  name: string;
  pathPattern: string;
  windowMs: number;
  maxRequests: number;
  keyBy: 'ip' | 'userId' | 'apiKey';
  burstAllowance?: number;
  createdAt: string;
}

export interface CreateRateLimitPolicyRequest {
  name: string;
  pathPattern: string;
  windowMs: number;
  maxRequests: number;
  keyBy: 'ip' | 'userId' | 'apiKey';
  burstAllowance?: number;
}

export interface RbacPolicy {
  policyId: string;
  name: string;
  roles: string[];
  resource: string;
  actions: string[];
  effect: 'allow' | 'deny';
  conditions?: Record<string, unknown>;
  createdAt: string;
}

export interface CreateRbacPolicyRequest {
  name: string;
  roles: string[];
  resource: string;
  actions: string[];
  effect: 'allow' | 'deny';
  conditions?: Record<string, unknown>;
}

export interface AuditLogEntry {
  logId: string;
  principal: string;
  action: string;
  resource: string;
  status: 'success' | 'failure';
  statusCode?: number;
  correlationId: string;
  path?: string;
  ipAddress?: string;
  userAgent?: string;
  errorCode?: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export interface AuditLogListResponse {
  data: AuditLogEntry[];
  meta: PaginationMeta;
}

// ---- Gateway internals ----

export interface GatewayRequest {
  requestId: string;
  apiVersion?: string;
  authContext?: AuthContext;
  startTime: number;
}

export interface PolicyDecision {
  allow: boolean;
  reason?: string;
  policyId?: string;
}

export interface AuditLogEvent {
  principal: string;
  action: string;
  resource: string;
  status: 'success' | 'failure';
  correlationId: string;
  path?: string;
  ipAddress?: string;
  userAgent?: string;
  statusCode?: number;
  errorCode?: string;
  metadata?: Record<string, unknown>;
}

// ---- Health ----

export interface DependencyHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  latencyMs?: number;
  error?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  dependencies: DependencyHealth[];
}

export interface GatewayInfo {
  name: string;
  version: string;
  environment: string;
  supportedApiVersions: string[];
  deprecatedApiVersions: string[];
  documentationUrl?: string;
}

// ---- WebSocket events ----

export interface WsServerEvent {
  type: 'connection.ack' | 'notification.new' | 'notification.updated' | 'pong' | 'error';
  payload: unknown;
  timestamp: string;
}

export interface WsClientEvent {
  type: 'notification.read' | 'ping';
  payload?: unknown;
}

// ---- Rate limit result ----

export interface RateLimitResult {
  allowed: boolean;
  limit: number;
  remaining: number;
  resetAt: number; // unix timestamp seconds
  retryAfter?: number; // seconds
}

// ---- Circuit breaker state ----

export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';
