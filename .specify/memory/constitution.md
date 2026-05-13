Quality principles
- MVP focus: exclude any payment/billing/subscription capability from UI. No “hidden” or disabled payment controls; remove, don’t just hide.
- Safety first: removing UI must not introduce navigation dead-ends or runtime errors. Build must succeed after removals.
- Accessibility: after removals, tab orders, landmarks, and semantics remain correct; no orphaned aria-controls/labels.
- Observability: remove payment-related telemetry; ensure dashboards/alerts don’t expect them.
- Performance: bundle size should not include payment code; tree-shake or delete dead payment modules.
- Security & privacy: ensure no client collects, stores, or transmits payment-related data (PAN, tokens). No residual logs or analytics fields for payments.
- Internationalization: remove orphaned payment translation keys and references.
- Testing: add negative tests asserting absence of payment UI across screens and routes.
- Documentation: update user guides and release notes to reflect absence of payment features in MVP.

Tech guardrails and coding standards
- Prefer deletion over feature-flag hiding for UI code. If retained for reintroduction, isolate behind a compile-time flag ENABLE_PAYMENTS=false and ensure code is excluded from bundles.
- No dangling imports, exports, routes, or deep links to removed features. CI lints with no-unused-vars/imports must pass.
- Navigation integrity: if a route is removed, ensure no link points to it; external deep links should resolve to 404 with standard UX.
- API clients: remove or deprecate payment client methods; no calls from UI code paths. Maintain type safety; build must have zero type errors.
- Logging/analytics: remove events and schemas referencing payment. Don’t leave null/undefined placeholders in event streams.
- Backwards compatibility: do not break non-payment features. Maintain existing public API contracts unless otherwise specified.

Non-functional requirements
- Reliability: 99.9% availability target unaffected. No runtime exceptions from missing components.
- Performance: First Contentful Paint and bundle size should not regress; payment code should not be included in final bundles.
- Security: No collection or processing of payment data. Ensure CSP and permissions are not widened for payment vendors (e.g., Stripe, PayPal).
- Compliance: No PII for payments appears in UI, logs, or analytics.
- Traceability: commits reference JT-5958/US-001; changes are gated by PR review and CI.

Acceptance testing principles
- Negative UI assertions: on every screen, confirm absence of payment-related strings and controls (e.g., “Billing”, “Payment”, “Upgrade”, “Subscribe”, “Credit card”).
- Navigation coverage: navbar, settings, profile, onboarding, empty states, modals, and error states.

Change management
- Produce a removal inventory PR description listing deleted files and routes.
- Update CHANGELOG and user docs to state payments are excluded from MVP.
- Ensure feature toggle defaults to disabled in all environments, if any remains.