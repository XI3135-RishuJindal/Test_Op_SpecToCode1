import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import CircuitBreaker from 'opossum';
import { config } from '../config';
import { logger } from './logger';

export interface HttpResponse<T = unknown> {
  status: number;
  headers: Record<string, string | string[] | undefined>;
  data: T;
}

type AxiosFn = (url: string, options: AxiosRequestConfig) => Promise<AxiosResponse>;

function createCircuitBreaker(name: string, fn: AxiosFn): CircuitBreaker<[string, AxiosRequestConfig], AxiosResponse> {
  const breaker = new CircuitBreaker(fn, {
    name,
    timeout: config.proxy.upstreamTimeoutMs,
    errorThresholdPercentage: 50,
    resetTimeout: config.proxy.circuitBreakerResetMs,
    volumeThreshold: config.proxy.circuitBreakerThreshold,
  });

  breaker.on('open', () => logger.warn({ service: name }, 'Circuit breaker OPEN'));
  breaker.on('halfOpen', () => logger.info({ service: name }, 'Circuit breaker HALF_OPEN'));
  breaker.on('close', () => logger.info({ service: name }, 'Circuit breaker CLOSED'));

  return breaker;
}

export class HttpClient {
  private readonly axiosInstance: AxiosInstance;
  private readonly breaker: CircuitBreaker<[string, AxiosRequestConfig], AxiosResponse>;

  constructor(baseUrl: string, serviceName: string) {
    this.axiosInstance = axios.create({
      baseURL: baseUrl,
      timeout: config.proxy.upstreamTimeoutMs,
    });

    const axiosFn: AxiosFn = (url, options) => this.axiosInstance.request({ url, ...options });
    this.breaker = createCircuitBreaker(serviceName, axiosFn);
  }

  async send<T = unknown>(
    method: string,
    path: string,
    options: {
      headers?: Record<string, string>;
      body?: unknown;
      params?: Record<string, string>;
    } = {},
  ): Promise<HttpResponse<T>> {
    const requestConfig: AxiosRequestConfig = {
      method,
      headers: options.headers,
      data: options.body,
      params: options.params,
    };

    const response = await this.breaker.fire(path, requestConfig) as AxiosResponse<T>;

    return {
      status: response.status,
      headers: response.headers as Record<string, string | string[] | undefined>,
      data: response.data,
    };
  }

  isOpen(): boolean {
    return this.breaker.opened;
  }
}

// Pre-built clients for each upstream service
export const upstreamClients = {
  userProfile: new HttpClient(config.upstreams.userProfile, 'user-profile-service'),
  mfa: new HttpClient(config.upstreams.mfa, 'mfa-service'),
  reporting: new HttpClient(config.upstreams.reporting, 'reporting-service'),
  payment: new HttpClient(config.upstreams.payment, 'payment-service'),
  notification: new HttpClient(config.upstreams.notification, 'notification-service'),
};
