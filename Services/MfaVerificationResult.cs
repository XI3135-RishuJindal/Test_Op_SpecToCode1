```csharp
namespace ApiGateway.Services
{
    public class MfaVerificationResult
    {
        public bool Success { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
```

### Explanation
- **AuthController.cs**: Added a new endpoint `VerifyMfaCode` to verify MFA codes. It checks input validity and uses an `IMfaService` to verify the code.
- **MfaCodeRequest.cs**: A model to represent the request data needed for verifying an MFA code.
- **IMfaService.cs**: Interface for the MFA service that contains the `VerifyCodeAsync` method that checks the validity of an MFA code.
- **MfaVerificationResult.cs**: A simple class to encapsulate the result of verifying an MFA code, including a success flag and an error message if applicable.

With these changes, the AuthController is equipped to handle MFA code verification, continuing the login process upon successful verification and handling errors appropriately.