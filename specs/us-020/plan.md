Approach and architecture
- Introduce a ProvisioningController exposing POST /api/provisioning/jit. The controller validates payload, generates or reads a RequestId (X-Request-ID), and delegates to IProvisioningOrchestrator.
- Implement ProvisioningOrchestrator with:
  - Transaction boundary via TransactionScope with TransactionScopeAsyncFlowOption.Enabled.
  - Steps: StageAccount, AssignPlan, Persist, PostCreateHooks (simulated). Each step records a compensating action. On success, Commit; on failure, run compensations and rethrow a domain exception.
  - Downstream call simulation with Task.Delay honoring CancellationToken and configurable timeout.
- Centralize error handling:
  - Add ExceptionHandlingMiddleware that maps domain exceptions and unhandled exceptions to ErrorResponse and sets X-Request-ID.
  - Map timeout exceptions to DownstreamTimeout; all others to ProvisioningFailed.
- Auditing:
  - Add IAuditLogger and SerilogAuditLogger to emit structured audit events at the end of success or on catch in orchestrator, with standard properties (RequestId, Outcome, ErrorCode, Duration).
  - Reuse Serilog setup; optionally add a dedicated file sink if needed.

API/data models
- Models/ProvisioningRequest.cs
- Models/ProvisioningResponse.cs
- Models/AuditLogEntry.cs (internal DTO for audit logger)

Configuration
- appsettings.json: Provisioning: { DefaultTimeoutSeconds: 2 } to bound downstream operations.
- Optional Serilog additional File sink to logs/provisioning-audit-.txt.

Registration and pipeline
- Program.cs:
  - services.AddScoped<IProvisioningOrchestrator, ProvisioningOrchestrator>();
  - services.AddSingleton<IAuditLogger, SerilogAuditLogger>();
  - app.UseMiddleware<ExceptionHandlingMiddleware>();
  - Add correlation ID enrichment: if X-Request-ID absent, generate and attach to HttpContext.Items and response header.

Testing
- Unit tests:
  - Tests/Controllers/ProvisioningControllerTests.cs: success, validation error, simulated internal error (500), and timeout (500 DownstreamTimeout).
  - Tests/Services/ProvisioningOrchestratorTests.cs: ensures Commit not called on failure by mocking a IUnitOfWork-like inner dependency or inspecting orchestrator’s internal state and compensation invocation.
- Ensure tests assert standardized error shape and presence of X-Request-ID.

Files/classes by repository XI3135-RishuJindal/Test_Op_SpecToCode1
- Add Controllers/ProvisioningController.cs.
- Add Services/IProvisioningOrchestrator.cs and Services/ProvisioningOrchestrator.cs.
- Add Services/IAuditLogger.cs and Services/SerilogAuditLogger.cs.
- Add Middleware/ExceptionHandlingMiddleware.cs.
- Add Models/ProvisioningRequest.cs, Models/ProvisioningResponse.cs, Models/AuditLogEntry.cs.
- Modify Program.cs to wire middleware and services; optionally update Serilog sinks.
- Add tests under Tests/Controllers/ProvisioningControllerTests.cs and Tests/Services/ProvisioningOrchestratorTests.cs.
- Update README.md to document new endpoint and failure semantics.

Delivery steps
1) Define domain and error taxonomy; create models and interfaces.
2) Implement middleware and orchestrator with transaction and compensation behavior.
3) Implement controller and register services.
4) Write comprehensive tests for success and failure paths.
5) Test locally with curl and JWT; validate logs and headers.
6) Update documentation and configurations.