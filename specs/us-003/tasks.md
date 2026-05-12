Repository: XI3135-RishuJindal/Test_Op_SpecToCode1
- [ ] add Tests/Compliance/RouteInventoryTests.cs: Reflection-based tests to enumerate routes and assert absence of payment/webhook endpoints; also assert no payment/webhook SDK packages in ApiGateway.csproj.
- [ ] add docs/ROUTE_INVENTORY.md: Human-readable route inventory with explicit statement that no payment endpoints or webhooks exist in MVP.
- [ ] modify README.md: Add link to docs/ROUTE_INVENTORY.md and brief instructions to run tests to verify the audit.
- [ ] add .specify/memory/README-US-003.txt: Short summary of the audit outcome and how the guardrail tests work for future contributors.