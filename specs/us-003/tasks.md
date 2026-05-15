Repository: XI3135-RishuJindal/Test_Op_SpecToCode1

Test enforcement
- [ ] add Tests/RouteInventoryTests.cs: implement reflection-based scanner that discovers all [ApiController] classes and their HTTP actions, resolves route templates (class-level + method-level), and fails if any prohibited keywords are detected in controller/action names or route templates
- [ ] add Tests/RouteDiscovery.cs: helper to encapsulate attribute parsing, [controller] token substitution, and auth detection ([Authorize]/[AllowAnonymous])
- [ ] run dotnet test locally and ensure the new tests pass and list the discovered routes in test output

Documentation
- [ ] add openspec/changes/api-gateway/route-inventory.md: record current endpoints (method, route, controller.action, auth), audit date, and commit SHA
- [ ] update README.md: add “Route Inventory Guard” section linking to specs/audit-api-route-inventory/spec.md and openspec/changes/api-gateway/route-inventory.md, describing the banned keywords and how the test works

Review and governance
- [ ] review acceptance criteria with product owner and security lead; confirm the prohibited keyword list covers their concerns
- [ ] add PR checklist item in openspec/changes/api-gateway/tasks.md noting “Route Inventory tests pass; no payment/webhook routes present”
- [ ] ensure ApiGateway.sln includes the Tests project (already present); verify CI executes tests and, if missing, document how to run locally

Audit follow-ups (if violations are found)
- [ ] if any prohibited routes are discovered, remove or rename them and update the inventory before merging