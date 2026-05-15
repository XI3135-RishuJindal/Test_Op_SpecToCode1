Delivery approach

Architecture decisions
- Use compile-time reflection in the test project to discover controllers ([ApiController]) and HTTP method attributes (HttpGet, HttpPost, HttpPut, HttpDelete, HttpPatch, HttpHead, HttpOptions).
- Resolve route templates by combining class-level [Route("api/[controller]")] with method-level templates (e.g., [HttpPost("token")]) and substituting [controller] with the controller name sans “Controller”.
- Determine authorization by checking for [Authorize] on controller or action; treat [AllowAnonymous] on the action as overriding.

Prohibited keyword enforcement
- Maintain a centralized, case-insensitive banned keyword list in the test.
- Assert that neither the resolved route, controller name, nor action name contains any banned term.
- On violation, fail the test and print the offending entries and the full discovered route list.

Artifacts and documentation
- Create a human-readable route inventory document capturing:
  - The discovered routes in the current commit
  - Per-route auth requirement
  - Audit date and commit SHA placeholder to be filled during PR
- Update README with a Route Inventory Guard section linking to the spec and inventory.

Implementation details
- Files to add under Tests:
  - Tests/RouteInventoryTests.cs: The xUnit test that scans and asserts.
  - Optionally a small helper class inside the same file or a new file (Tests/RouteDiscovery.cs) to keep logic readable.
- Do not modify runtime code paths for this story. The enforcement is test-only and documentation.
- Keep the test deterministic by avoiding server bootstrapping; rely solely on reflection of attribute metadata.

Current expected inventory (from code context)
- POST api/auth/token (anonymous)
- GET api/health (anonymous)
- POST api/test (requires authorization)

Process
- Implement tests locally, run dotnet test to validate.
- Capture the inventory into a markdown file under openspec/changes/api-gateway/route-inventory.md during PR, including the commit SHA.
- Have product and security reviewers sign off on the inventory and acceptance criteria.

Rollout and verification
- Open PR with tests and docs.
- Ensure CI runs tests and they pass.
- Post-merge, any future introduction of banned endpoints will fail tests automatically.