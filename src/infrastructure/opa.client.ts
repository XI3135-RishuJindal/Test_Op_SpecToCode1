import axios, { AxiosInstance } from 'axios';
import { config } from '../config';
import { logger } from './logger';
import { PolicyDecision } from '../types';

export interface OpaInput {
  principal: {
    userId: string;
    roles: string[];
    scopes: string[];
  };
  resource: string;
  action: string;
  context?: Record<string, unknown>;
}

export class OpaClient {
  private readonly http: AxiosInstance;

  constructor() {
    this.http = axios.create({
      baseURL: config.opa.url,
      timeout: config.opa.timeoutMs,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async evaluate(input: OpaInput): Promise<PolicyDecision> {
    try {
      const response = await this.http.post<{ result: boolean | { allow: boolean; reason?: string } }>(
        config.opa.policyPath,
        { input },
      );

      const result = response.data.result;
      if (typeof result === 'boolean') {
        return { allow: result };
      }
      return {
        allow: result?.allow ?? false,
        reason: result?.reason,
      };
    } catch (err) {
      logger.error({ err }, 'OPA evaluation failed — defaulting to deny');
      // Fail-safe: deny on OPA unavailability
      return { allow: false, reason: 'Policy engine unavailable' };
    }
  }
}

export const opaClient = new OpaClient();
