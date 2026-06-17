## Architecture Plan

- **Endpoint:** Add a new `POST /api/auth/register` endpoint to `AuthController`.
- **Model:** Create a `RegisterEmailRequest` model with a required `Email` field.
- **Validation:** Use regex (close to RFC 5322) for high-fidelity email format checks in the controller or, preferably, a dedicated validator/service class.
- **Email Service:** Introduce an `IEmailSender` interface + mock implementation for sending verification emails (log to console/file for now).
- **Separation:** Place validation and email logic in separate classes/services for testability.
- **Error Handling:** All error responses use the existing `ErrorResponse` type; catch and log exceptions.
- **Testing:** Add/extend tests in `Tests/Controllers/AuthControllerTests.cs` to cover all branch logic using Moq for the email sender.
- **Documentation:** Add XML/Swagger documentation for the new endpoint.
- **Config:** Email sender config (dummy/no-op for now); note where real integration would go.

File-level changes:
- `Controllers/AuthController.cs`: Add new endpoint, inject email service.
- `Models/RegisterEmailRequest.cs`: New request model.
- New: `Services/IEmailSender.cs`, `Services/MockEmailSender.cs`
- `Tests/Controllers/AuthControllerTests.cs`: Extend to cover new scenarios.