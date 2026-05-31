import { opaClient, OpaInput } from '../infrastructure/opa.client';
import { PolicyDecision } from '../types';
import { logger } from '../infrastructure/logger';

export interface RbacEvaluationInput {
  principal: {
    userId: string;
    roles: string[];
    scopes: string[];
  };
  resource: string;
  action: string;
  requiredScopes?: string[];
}

export class RbacService {
  /**
   * Evaluates an RBAC/ABAC decision.
   * First checks required scopes locally (fast path), then delegates to OPA.
   */
  async evaluate(input: RbacEvaluationInput): Promise<PolicyDecision> {
    // Fast path: check required scopes directly
    if (input.requiredScopes && input.requiredScopes.length > 0) {
      const hasScope = input.requiredScopes.some(
        (scope) =>
          input.principal.scopes.includes(scope) ||
          input.principal.roles.includes('admin') ||
          input.principal.scopes.includes('admin'),
      );

      if (!hasScope) {
        return {
          allow: false,
          reason: `Required scope(s): ${input.requiredScopes.join(', ')}`,
        };
      }
    }

    // Delegate to OPA for fine-grained policy evaluation
    const opaInput: OpaInput = {
      principal: input.principal,
      resource: input.resource,
      action: input.action,
    };

    const decision = await opaClient.evaluate(opaInput);

    if (!decision.allow) {
      logger.debug({ input, decision }, 'RBAC denied by OPA');
    }

    return decision;
  }

  /**
   * Checks if a principal has admin-level access.
   */
  isAdmin(roles: string[], scopes: string[]): boolean {
    return (
      roles.includes('admin') ||
      scopes.includes('admin') ||
      scopes.includes('admin:gateway')
    );
  }
}
