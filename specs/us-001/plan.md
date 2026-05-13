Architecture and approach
- Strategy: Physically remove payment UI code (preferred). Where retention is necessary for future reintroduction, gate behind a compile-time flag ENABLE_PAYMENTS=false and ensure code is tree-shaken from production bundles.
- Navigation cleanup: Remove routes, menu items, deep links. Ensure 404 handling is consistent for legacy deep-link URIs.
- Analytics cleanup: Remove payment event constants and invocations; assert no payment events are emitted in tests.
- API client hygiene: Remove payment API calls from UI code paths. Keep generated clients if shared with other apps, but mark payment methods @deprecated and add no-usage assertions in the web/mobile codebases.
- Translations: Remove payment keys and associated usage; retain language packs integrity.
- Third-party SDKs: If exclusively used by removed UI (e.g., Stripe.js), remove import and dependency; otherwise defer removal to separate ticket if shared.

Component design and changes by repository

acme/web-frontend
- Routing
  - Remove routes: /billing, /subscribe, /payment-methods.
  - Update src/routes/index.tsx to remove Route entries and lazy imports.
- Components
  - Delete PaymentButton, PaymentForm, BillingPage, ManageSubscriptionModal.
  - Update Navbar/Header and Settings to remove links/sections to billing.
- State/feature flags
  - Remove payment-related feature flag checks from components; ensure ENABLE_PAYMENTS defaults false where present.
- Analytics
  - Remove payment-related events from src/analytics/events.ts and their invocations.
- I18n
  - Remove payment translation namespace/file and keys; ensure no dangling references.
- Tests
  - Remove obsolete tests that referenced payment flows.
  - Add an e2e test asserting absence of payment UI across key surfaces.
- Build
  - Verify treeshaking excludes any leftover payment modules; ensure bundle report shows reduction.

acme/mobile-app
- Navigation
  - Remove PaymentStack and routes from app/navigation/Routes.ts.
- Screens and components
  - Delete PaymentScreen, BillingScreen, ManageSubscriptionSheet.
  - Remove Settings menu items related to payments.
- Deep links
  - Remove associated scheme handlers (e.g., myapp://billing).
- Analytics
  - Delete payment event constants and calls.
- Tests
  - Add e2e test to assert absence in Settings and main menu.

acme/api-service
- No functional change required for backend.
- Optional: Mark payment endpoints with x-internal: true in OpenAPI to prevent future client-surface leaks.
- Documentation note in README to reflect UI removal for MVP.

acme/docs
- Update user-guide navigation and settings sections to remove billing references.
- Update release notes for MVP to state payments are excluded.

API contracts
- No new APIs.
- If OpenAPI updated: only annotations; no breaking changes. Client generation unaffected for non-payment domains.

Data model changes
- None.

Testing strategy
- Unit tests: Ensure components compile without payment imports; verify Navbar/Settings do not render payment items.
- E2E web (Playwright or Cypress):
  - Assert absence of payment terms in nav/settings.
  - Direct navigation to /billing returns 404 page.
- E2E mobile (Detox/Appium):
  - Assert payment items are not present in menus/settings.
- Static analysis:
  - Grep-based CI check to fail build if forbidden terms appear in UI text: /(payment|billing|upgrade|subscribe)/i excluding docs and tests where intended.
- Analytics verification:
  - Snapshot test of exported event names ensures no payment events.

Risk mitigation
- Risk: Hidden imports cause build failure.
  - Mitigation: Type-safe removal, run TS/flow and lints locally and in CI.
- Risk: External links or deep links break UX.
  - Mitigation: Provide 404 for removed web routes; remove mobile deep link handlers.
- Risk: Orphaned translations.
  - Mitigation: i18n extraction check must pass; remove unused namespaces.

Rollout plan
- Single PR per repo with clear “Removal Inventory” section.
- Coordinate merges to avoid broken deep links in mobile/web cross-refs.
- Post-merge smoke tests on staging; sign-off by Product.

Implementation notes
- Use semantic commit messages: feat(web): remove payment UI (JT-5958).
- Ensure environment configs set ENABLE_PAYMENTS=false or remove flag usage entirely.
- Update CHANGELOG entries with “Removed” section.