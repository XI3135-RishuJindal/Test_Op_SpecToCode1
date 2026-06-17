**XI3135-RishuJindal/Test_Op_SpecToCode1**

- [ ] add Models/RegisterEmailRequest.cs: define request DTO for email registration
- [ ] add Services/IEmailSender.cs: define interface for sending emails
- [ ] add Services/MockEmailSender.cs: implement mock service for development/testing environment
- [ ] modify Controllers/AuthController.cs: add POST /api/auth/register endpoint, inject IEmailSender, perform email validation and trigger email send
- [ ] update Startup/Program.cs: register IEmailSender in DI container
- [ ] add unit tests in Tests/Controllers/AuthControllerTests.cs: validate correct/incorrect email scenarios, verify error and happy path, simulate email send failures
- [ ] add XML comments to new endpoint and new types for swagger support
- [ ] update README.md: document the new endpoint, request body, and error cases