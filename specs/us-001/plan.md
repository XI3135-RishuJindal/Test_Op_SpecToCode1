Architecture and approach
- Preventive, test-driven enforcement: Add invariant tests that scan the API assembly for any route templates or action identifiers containing payment-related terminology. Also scan common UI asset folders if they exist.
- Centralize the banned terms list in a repo file to enable easy updates without code changes.
- Minimal code changes: Expose Program as a partial class only if needed for test assembly discovery; no runtime behavior changes.

Components impacted
- ApiGateway (this repository)
  - Tests: New non-functional test suite to enforce absence of payment UI elements.
  - Optionally expose Program partial class to support certain test patterns (though reflection-based scanning does not require server bootstrapping).

Data model and API contracts
- No changes to models or endpoints; this is a scope guardrail.
- No new endpoints added.

Banned term policy
-